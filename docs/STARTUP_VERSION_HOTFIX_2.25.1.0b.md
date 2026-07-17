# 2.25.1.0b — Startup Version Hotfix

Restores the complete central version API required by the runtime:

- `PRODUCT_NAME`
- `VERSION`
- `APP_TITLE`
- `SIDEBAR_VERSION`
- `APP_USER_MODEL_ID`
- `version_info()`

The previous 2.25.1.0a overlay accidentally replaced `version.py` with a reduced
variant. Unit tests imported only `VERSION`, so the missing runtime constants were
not detected until the real application startup imported `app.py`.
