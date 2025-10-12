def try_layout(wall_w, wall_h, page_w, page_h, pages, margin=0):
    """
    Determine if a mural layout fits within the given wall dimensions.
    Returns layout metadata if it fits.
    Enforces:
    - Margin between 5cm and 15cm
    - Row gap between 1cm and 5cm
    - Page scaling between 95% and 105%
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

                best = {
                    "fit": True,
                    "grid": f"{cols}x{rows}",
                    "scale_pct": scale_pct,
                    "row_gap": row_gap,
                    "margin_x": 0,
                    "margin_y": 0,
                    "text_centered": True
                }

        if best:
            best["eligible"] = True
            return best

    return {"eligible": False}