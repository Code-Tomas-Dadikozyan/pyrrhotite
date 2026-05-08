/**
 * Schoenflies
 * Copyright (c) 2022 Luuk Kempen
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include "freetype_font.h"

/**
 * @brief Construct a new FreeTypeFont object
 */
FreeTypeFont::FreeTypeFont() {}

/**
 * @brief Initialize the FreeType font and character textures
 */
void FreeTypeFont::initialize() {
    File file(this->font_path);
    std::string font_str = file.get_stream().str();
    const char* font = font_str.c_str();
    unsigned int font_size = font_str.size();

    FT_Library ft;
    if (FT_Init_FreeType(&ft)) {
        throw std::runtime_error("Could not initialize FreeType library");
    }

    FT_Face face;
    if (FT_New_Memory_Face(ft, (const FT_Byte*) font, font_size, 0, &face)) {
        throw std::runtime_error("Could not load font");
    }

    FT_Set_Pixel_Sizes(face, 0, 128);

    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    f->glPixelStorei(GL_UNPACK_ALIGNMENT, 1);  // disable byte-alignment restriction

    for (unsigned char c = this->min_char; c <= this->max_char; ++c) {
        if (FT_Load_Char(face, c, FT_LOAD_RENDER)) {
            throw std::runtime_error("Could not load glyph " + c);
        }

        FT_GlyphSlot& glyph = face->glyph;
        unsigned int texture;
        f->glGenTextures(1, &texture);
        f->glBindTexture(GL_TEXTURE_2D, texture);
        f->glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, glyph->bitmap.width, glyph->bitmap.rows, 0, GL_RED, GL_UNSIGNED_BYTE, glyph->bitmap.buffer);

        f->glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        f->glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        f->glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        f->glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

        Character character = {
            (int) texture,
            glm::ivec2(glyph->bitmap.width, glyph->bitmap.rows),
            glm::ivec2(glyph->bitmap_left, glyph->bitmap_top),
            (unsigned int) glyph->advance.x
        };
        this->characters.emplace(c, character);
    }

    FT_Done_Face(face);
    FT_Done_FreeType(ft);

    this->initialized = true;
}

/**
 * @brief Get the character object
 *
 * @param c character
 * @return Character
 */
Character FreeTypeFont::get_character(char c) {
    if (!this->initialized) {
        throw std::runtime_error("Font not initialized");
    }
    if (c < this->min_char || c > this->max_char) {
        throw std::runtime_error("Invalid character requested: " + c);
    }
    return this->characters[c];
}

/**
 * @brief Get the size of a string
 *
 * @param string
 * @return glm::ivec2
 */
glm::ivec2 FreeTypeFont::get_string_size(std::string& string) {
    glm::ivec2 size = glm::ivec2(0, 0);
    for (unsigned int i = 0; i < string.size(); ++i) {
        Character ch = this->get_character(string[i]);
        size.x += 2 * ch.advance / 64;
        if (ch.bearing.y > size.y) size.y = ch.bearing.y;
    }
    return size;
}
