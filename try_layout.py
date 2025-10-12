def try_layout(wall_w, wall_h, page_w, page_h, pages, margin=0):
    """
    Returns layout metadata if the mural fits within the wall dimensions.
    Enforces:
    - Margin between 5–15 cm
    - Page scaling between 95–105%
    - Row gap between 1–5 cm
    - Rejects sparse layouts that inflate grid size
    """

    for margin_test in range(5, 16):  # test margins from 5 to 15 cm
        usable_w = wall_w - 2 * margin_test
        usable_h = wall_h - 2 * margin_test

        best = None
        for cols in range(1, pages + 1):
            rows = (pages + cols - 1) // cols  # ceiling division
            mural_w = cols * page_w
            mural_h = rows * page_h

            if mural_w <= usable_w and mural_h <= usable_h:
                scale_w = usable_w / mural_w
                scale_h = usable_h / mural_h
                scale_pct = int(min(scale_w, scale_h) * 100)

                # ✅ Enforce scale between 95% and 105%
                if not (95 <= scale_pct <= 105):
                    continue

                # ✅ Enforce row gap between 1 and 5 cm
                row_gap = 3
                if not (1 <= row_gap <= 5):
                    continue

                # ✅ Reject sparse layouts (e.g. 15x1 or 1x15)
                if cols == 1 or rows == 1:
                    continue

                best = {
                    "fit": True,
                    "grid": f"{cols}x{rows}",
                    "scale_pct": scale_pct,
                    "row_gap": row_gap,
                    "margin_x": margin_test,
                    "margin_y": margin_test,
                    "text_centered": True
                }

        if best:
            best["eligible"] = True
            return best

    return {"eligible": False}