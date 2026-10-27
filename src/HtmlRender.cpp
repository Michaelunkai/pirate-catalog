/**
 * HtmlRender.cpp — Render embedded HTML to HDC / GDI
 * Location: F:\study\projects\pirate-catalog
 */

#include "../include/BootyCatalog.h"
#include <vector>
#include <string>

namespace HtmlRender {

std::string generate_full_html(void) {
    int cssLen = 0, jsLen = 0, jsdlLen = 0;
    const char* css = (const char*)find_resource(GetModuleHandleA(NULL), 1003, RT_RCDATA, &cssLen);
    const char* js  = (const char*)find_resource(GetModuleHandleA(NULL), 1004, RT_RCDATA, &jsLen);
    const char* jsdl = (const char*)find_resource(GetModuleHandleA(NULL), 1005, RT_RCDATA, &jsdlLen);

    std::string html;
    html = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
           "  <meta charset=\"UTF-8\">\n"
           "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
           "  <title>Booty Catalog</title>\n"
           "  <style>\n";
    html += css ? css : "";
    html += "\n  </style>\n</head>\n<body>\n";
    html += (const char*)find_resource(GetModuleHandleA(NULL), 1002, RT_RCDATA, &cssLen);
    html += "\n  <script>\n";
    html += js ? js : "";
    html += "\n  </script>\n"
           "  <script>\n";
    html += jsdl ? jsdl : "";
    html += "\n  </script>\n"
           "</body>\n</html>\n";

    return html;
}

void generate_game_card_html(char* buf, int bufSize, Game* g) {
    if (!g || !buf) return;
    int i = 0;
    i += sprintf(buf + i, "<div class=\"game-card\" data-id=\"%s\">\n", g->id);
    i += sprintf(buf + i, "  <div class=\"card-image\" style=\"background: %s;\"></div>\n",
                 g->imageGradient[0] ? g->imageGradient : "linear-gradient(135deg, #1a2744, #2c3e6b)");
    i += sprintf(buf + i, "  <div class=\"card-body\">\n");
    i += sprintf(buf + i, "    <div class=\"card-title\">%s</div>\n", g->title);
    i += sprintf(buf + i, "    <div class=\"card-genre\">%s</div>\n", g->genreLabel);
    i += sprintf(buf + i, "    <div class=\"card-desc\">%s</div>\n", g->description);
    i += sprintf(buf + i, "    <div class=\"card-meta\">%s / %s / %s</div>\n",
                 g->crackedDate, g->crackedBy, g->size);
    i += sprintf(buf + i, "  </div>\n</div>\n");
    buf[i] = '\0';
}

void render_to_hdc(HDC hdc, RECT* rect, const std::string& html) {
    SetTextColor(hdc, RGB(0x63, 0xb3, 0xed));
    SetBkMode(hdc, TRANSPARENT);
    TextOutA(hdc, rect->left + 20, rect->top + 10, APP_NAME, (int)strlen(APP_NAME));

    char count[128];
    sprintf(count, "Showing %d games from all repacker sources", g_gameCount);
    SetTextColor(hdc, RGB(0xa8, 0xb8, 0xcc));
    TextOutA(hdc, rect->left + 20, rect->top + 40, count, (int)strlen(count));

    SetTextColor(hdc, RGB(0x7e, 0xc8, 0x7e));
    TextOutA(hdc, rect->left + 20, rect->bottom - 30, "All systems operational", 22);
}

std::string html_escape(const std::string& s) {
    std::string out;
    for (size_t i = 0; i < s.length(); i++) {
        char c = s[i];
        switch (c) {
            case '<': out += "&lt;"; break;
            case '>': out += "&gt;"; break;
            case '&': out += "&amp;"; break;
            case '"': out += "&quot;"; break;
            default:  out += c; break;
        }
    }
    return out;
}

} // namespace HtmlRender
