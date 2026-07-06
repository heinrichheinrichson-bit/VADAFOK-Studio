# Architecture

## v2.8.2 Card Creator Styles

Card Creator now reuses the Style Engine.

Flow:
1. Load available style names via `style_engine.list_styles()`.
2. User selects a style for a field.
3. The style is loaded via `style_engine.load_style()`.
4. The template field is updated via `style_engine.apply_style()`.
5. The template is saved.
6. Card preview is re-rendered.

Important:
- This changes the template's visual style.
- It does not change card data text.
