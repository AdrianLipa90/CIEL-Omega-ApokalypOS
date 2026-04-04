This branch contains an instruction file to apply the local runtime-stable patch prepared by the assistant.

Patch file is available in the sandbox at:

sandbox:/mnt/data/CIEL-_SOT_Agent-main_local_fixed.patch

To apply locally after fetching the repo and checking out this branch:

1. Download the patch from the sandbox location onto your machine (or copy its contents into a file named CIEL_runtime_stable.patch).
2. From the repo root run:

   git apply CIEL_runtime_stable.patch
   git add -A
   git commit -m "Apply runtime-stable patch prepared by assistant"
   git push origin fix/runtime-stable-20260404

3. Open a Pull Request on GitHub from branch `fix/runtime-stable-20260404` into `main` and merge when ready.

If you want, I can also create a PR body here and open the PR for you. Let me know and I'll proceed.
