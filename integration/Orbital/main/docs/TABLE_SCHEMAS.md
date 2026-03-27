# Table Schemas

## runtime_files.csv
- canonical_path
- extension
- size_bytes
- line_count
- py_functions
- py_classes
- import_in_repo_count
- import_external_count
- contains_phase
- contains_memory
- contains_reduction
- contains_truth
- contains_holonomy
- contains_tau
- contains_registry
- contains_constraint
- contains_potential
- contains_orchestrator

## runtime_functions.csv
- file_path
- qualname
- function_name
- class_name
- arg_count
- decorator_count
- returns_value
- touches_state
- touches_memory
- touches_phase
- touches_reduction
- touches_registry
- touches_io

## formal_symbols.csv
- symbol
- meaning
- source_type
- source_name
- status
- category
- equation_or_note

## symbol_to_runtime_map.csv
- symbol
- runtime_path
- runtime_object
- mapping_type
- confidence
- note

## orchestrator_graph_edges.csv
- src
- dst
- edge_type

## phase_couplings.csv
- object
- role
- depends_on
- feeds_into
- status
- note
