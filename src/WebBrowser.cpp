/**
 * WebBrowser.cpp — Browser component (CEF/WebView2/ActiveX/GDI fallback)
 * Location: F:\study\projects\pirate-catalog
 */

#include "../include/BootyCatalog.h"
#include <vector>
#include <string>

namespace WebBrowser {

void render_offline(HDC hdc, RECT* rect, int nGames) {
    HBRUSH bgBrush = CreateSolidBrush(RGB(0x0a, 0x0e, 0x17));
    FillRect(hdc, rect, bgBrush);
    DeleteObject(bgBrush);

    SetTextColor(hdc, RGB(0x63, 0xb3, 0xed));
    SetBkMode(hdc, TRANSPARENT);
    TextOutA(hdc, rect->left + 20, rect->top + 10, APP_NAME, (int)strlen(APP_NAME));

    std::string subtitle = "Showing " + std::to_string(nGames) + " games from all repacker sources";
    SetTextColor(hdc, RGB(0xa8, 0xb8, 0xcc));
    TextOutA(hdc, rect->left + 20, rect->top + 35, subtitle.c_str(), (int)subtitle.length());

    int cardW = 200, cardH = 280;
    int cols = (rect->right - rect->left - 40) / (cardW + 16);
    if (cols < 1) cols = 1;

    int y = rect->top + 70;
    int idx = 0;

    for (int i = 0; i < nGames && idx < g_gridCount; i++) {
        int col = idx % cols;
        int x = rect->left + 20 + col * (cardW + 16);

        GameItem* gi = &g_grid[idx];
        RECT cardRect = { x, y, x + cardW, y + cardH };

        HBRUSH cardBrush = CreateSolidBrush(RGB(0x15, 0x1d, 0x2e));
        FillRect(hdc, &cardRect, cardBrush);
        DeleteObject(cardBrush);

        int r = 0x1a, g_ = 0x27, b = 0x44;
        HBRUSH gradBrush = CreateSolidBrush(RGB(r, g_, b));
        RECT gradRect = { cardRect.left, cardRect.top, cardRect.right, cardRect.top + 60 };
        FillRect(hdc, &gradRect, gradBrush);
        DeleteObject(gradBrush);

        HPEN pen = CreatePen(PS_SOLID, 1, RGB(0x2a, 0x3a, 0x52));
        HPEN oldPen = (HPEN)SelectObject(hdc, pen);
        Rectangle(hdc, cardRect.left, cardRect.top, cardRect.right, cardRect.bottom);
        SelectObject(hdc, oldPen);
        DeleteObject(pen);

        SetTextColor(hdc, RGB(0xe8, 0xed, 0xf5));
        TextOutA(hdc, cardRect.left + 8, cardRect.top + 70,
                 gi->game.title, (int)strlen(gi->game.title));

        SetTextColor(hdc, RGB(0x63, 0xb3, 0xed));
        TextOutA(hdc, cardRect.left + 8, cardRect.top + 92,
                 gi->game.genreLabel, (int)strlen(gi->game.genreLabel));

        SetTextColor(hdc, RGB(0xa8, 0xb8, 0xcc));
        TextOutA(hdc, cardRect.left + 8, cardRect.top + 108,
                 gi->game.crackedBy, (int)strlen(gi->game.crackedBy));

        SetTextColor(hdc, RGB(0xf6, 0xc8, 0x47));
        char sizeBuf[32];
        sprintf(sizeBuf, "%s", gi->game.size);
        TextOutA(hdc, cardRect.left + 8, cardRect.top + 124, sizeBuf, (int)strlen(sizeBuf));

        if (gi->game.isJustDropped) {
            SetTextColor(hdc, RGB(0xf6, 0xc8, 0x47));
            TextOutA(hdc, cardRect.right - 50, cardRect.top + 8, "NEW", 3);
        }
        if (gi->game.isUpcoming) {
            SetTextColor(hdc, RGB(0xa7, 0x8b, 0xfa));
            TextOutA(hdc, cardRect.right - 60, cardRect.top + 8, "UP", 2);
        }

        idx++;
        if (col + 1 >= cols) {
            y += cardH + 16;
            if (y + cardH > rect->bottom) break;
        }
    }

    SetTextColor(hdc, RGB(0x7e, 0xc8, 0x7e));
    TextOutA(hdc, rect->left + 20, rect->bottom - 25, "All systems operational", 22);
}

} // namespace WebBrowser
