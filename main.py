













def list_available_pipelines():
    """testing 123"""
    pipeline_dir = Path(__file__).parent / 'configs' / 'pipelines'
    return [f.stem for f in pipeline_dir.glob('*.yaml')]

def set_active_pipeline(pipeline_name: str):
    """Set the active pipeline configuration"""
    active_file = Path(__file__).parent / 'configs' / 'active_pipeline.txt'
    with open(active_file, 'w') as f:
        f.write(pipeline_name)

def get_active_pipeline() -> str:
    """Get the name of the active pipeline configuration"""
    active_file = Path(__file__).parent / 'configs' / 'active_pipeline.txt'
    if not active_file.exists():
        return 'touch_rugby_basic' # default
    return active_file.read_text().strip()
