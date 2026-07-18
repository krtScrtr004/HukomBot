from mako.lookup import TemplateLookup
from backend.app.util.utility import get_project_root

PROJECT_ROOT = str(get_project_root())

lookup = TemplateLookup(
    directories=[f"{PROJECT_ROOT}/frontend"], input_encoding="utf-8"
)
