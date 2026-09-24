# NEON OS

NEON OS is a dual-target launcher and desktop shell built around the VOID/HORIZON interface direction and the existing Pulsar AI, Infinity OS, EXO, Ember and AEGIS/ASTER projects.

Star AI is intentionally excluded.

## Targets

- Android: default-home-capable launcher in `android/`
- Windows: unified desktop shell in `desktop/`
- Shared AI providers: Gemini, xKiro, Anthropic, OpenAI, Groq and OpenRouter
- Legacy-source import tooling: `tools/import_legacy_sources.py`

## Android

The Android target declares the HOME role, provides an installed-app drawer, NEON system controls, floating orb entry point, accessibility-service entry point and the shared provider nexus.

Build locally with:

```text
gradle -p android :app:assembleDebug
```

The following private Gradle properties can be injected at build time:

```text
NEON_GEMINI_API_KEY
NEON_XKIRO_API_KEY
NEON_ANTHROPIC_API_KEY
NEON_OPENAI_API_KEY
NEON_GROQ_API_KEY
NEON_OPENROUTER_API_KEY
```

Private key values are not stored in this public repository.

## Desktop

Run:

```text
cd desktop
python neon_os.py
```

Build the Windows executable:

```text
powershell -ExecutionPolicy Bypass -File desktop/build_windows.ps1
```

The desktop shell can load sanitized copies of the existing desktop projects from `desktop/vendor/`.

## CI

Every push to `main` builds an Android debug APK and a Windows desktop executable. Successful files are published as GitHub Actions artifacts.
