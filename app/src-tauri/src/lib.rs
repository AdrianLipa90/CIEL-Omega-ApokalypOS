use tauri::Manager;

#[tauri::command]
fn get_ciel_base() -> String {
    // Return empty string if not yet set; frontend will retry instead of caching a wrong default.
    std::env::var("CIEL_API_URL").unwrap_or_default()
}

fn find_python() -> Option<std::path::PathBuf> {
    use std::path::PathBuf;
    let home = std::env::var("HOME").ok().map(PathBuf::from)?;
    let mut candidates: Vec<PathBuf> = vec![
        // Primary project venv (most stable)
        home.join("Pulpit/CIEL_TESTY/venv/bin/python3.12"),
        home.join("Pulpit/CIEL_TESTY/venv/bin/python3"),
        // Legacy/temporary venv path used by some hooks
        PathBuf::from("/tmp/ciel_venv/bin/python3"),
    ];

    // Allow override for debugging / alternate installs.
    if let Ok(p) = std::env::var("CIEL_PY") {
        candidates.insert(0, PathBuf::from(p));
    }

    candidates.into_iter().find(|p| p.exists())
}

fn spawn_backend() {
    // Start the Flask GUI backend in the background (best-effort).
    // If it is already running (port occupied) or spawn fails, we do not crash the app;
    // frontend can still work against an existing backend.
    use std::fs::{create_dir_all, OpenOptions};
    use std::io::Write;
    use std::net::{TcpListener, TcpStream};
    use std::path::PathBuf;
    use std::time::Duration;

    let project_dir = "/home/adrian/Pulpit/CIEL_TESTY/CIEL1";

    // If caller already provided an API URL, don't spawn another backend.
    if std::env::var("CIEL_API_URL").ok().filter(|s| !s.is_empty()).is_some() {
        return;
    }

    let py = find_python().unwrap_or_else(|| PathBuf::from("python3"));

    // Log file for backend spawn + Python stderr/stdout.
    let log_dir = PathBuf::from("/home/adrian/Pulpit/CIEL_memories/logs");
    let _ = create_dir_all(&log_dir);
    let log_path = log_dir.join("tauri_backend.log");
    let mut header = OpenOptions::new().create(true).append(true).open(&log_path).ok();
    if let Some(h) = header.as_mut() {
        let ts = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0);
        let _ = writeln!(h, "\n===== spawn_backend unix_ts={} =====", ts);
        let _ = writeln!(h, "python={}", py.display());
    }

    // If backend is already running on the canonical port, reuse it.
    // This avoids leaving multiple Python servers behind after repeated launches.
    {
        let addr = std::net::SocketAddr::from(([127, 0, 0, 1], 2435u16));
        if TcpStream::connect_timeout(&addr, Duration::from_millis(120)).is_ok() {
            std::env::set_var("CIEL_API_URL", "http://127.0.0.1:2435");
            if let Ok(mut h) = OpenOptions::new().create(true).append(true).open(&log_path) {
                let _ = writeln!(h, "[spawn_backend] reusing existing backend on 127.0.0.1:2435");
            }
            return;
        }
    }

    // Try a small port range. Only publish CIEL_API_URL after we believe the server is alive.
    for port in 2435u16..2455u16 {
        // Skip ports that are clearly occupied.
        if TcpListener::bind(("127.0.0.1", port)).is_err() {
            continue;
        }

        let mut cmd = std::process::Command::new(&py);
        cmd.args([
            "-m",
            "ciel_sot_agent.gui.app",
            "--host",
            "127.0.0.1",
            "--port",
            &port.to_string(),
            "--root",
            project_dir,
        ])
        .current_dir(project_dir)
        .env("PYTHONUNBUFFERED", "1")
        .env(
            "PYTHONPATH",
            format!("{}/src:{}", project_dir, std::env::var("PYTHONPATH").unwrap_or_default()),
        )
        .env("CIEL_API_URL", format!("http://127.0.0.1:{}", port));

        // Redirect Python output to a file for debugging.
        if let Ok(f) = OpenOptions::new().create(true).append(true).open(&log_path) {
            if let Ok(f2) = f.try_clone() {
                cmd.stdout(f);
                cmd.stderr(f2);
            }
        }

        let mut child = match cmd.spawn() {
            Ok(c) => c,
            Err(_) => continue,
        };

        // Give the process a moment. If it exits immediately (e.g. "Address already in use"),
        // try the next port.
        std::thread::sleep(Duration::from_millis(250));
        if let Ok(Some(_status)) = child.try_wait() {
            continue;
        }

        // Verify we can connect (best-effort); this also avoids publishing dead ports.
        let mut ok = false;
        let addr = std::net::SocketAddr::from(([127, 0, 0, 1], port));
        for _ in 0..40 {
            if TcpStream::connect_timeout(
                &addr,
                Duration::from_millis(200),
            )
            .is_ok()
            {
                ok = true;
                break;
            }
            std::thread::sleep(Duration::from_millis(100));
        }

        if ok {
            std::env::set_var("CIEL_API_URL", format!("http://127.0.0.1:{}", port));
            if let Ok(mut h) = OpenOptions::new().create(true).append(true).open(&log_path) {
                let _ = writeln!(h, "[spawn_backend] backend alive on 127.0.0.1:{}", port);
            }
            return;
        }

        // If we can't connect, do not publish this port; try another.
        let _ = child.kill();
    }
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_http::init())
        .invoke_handler(tauri::generate_handler![get_ciel_base])
        .setup(|app| {
            spawn_backend();

            let window = app.get_webview_window("main").unwrap();
            window.set_title("CIEL/Ω — Control Panel").unwrap();
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running CIEL/Ω");
}
