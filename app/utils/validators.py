# small utilities (left intentionally light)
def clean_org_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")
