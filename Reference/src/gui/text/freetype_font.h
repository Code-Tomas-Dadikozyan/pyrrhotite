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

#ifndef GUI_TEXT_FREETYPE_FONT_H
#define GUI_TEXT_FREETYPE_FONT_H

#include <cstring>
#include <map>
#include <stdexcept>
#include <string>
#include <ft2build.h>
#include <freetype/freetype.h>
#include <glm/glm.hpp>
#include <QOpenGLContext>
#include <QOpenGLFunctions>
#include "../../file.h"
#include "character.h"

class FreeTypeFont {
private:
    const std::string font_path = ":/assets/fonts/OpenSans-Regular.ttf";

    bool initialized = false;
    std::map<unsigned char, Character> characters;

    const unsigned char min_char = 32;
    const unsigned char max_char = 127;

public:
    /**
     * @brief Construct a new FreeTypeFont object
     */
    FreeTypeFont();

    /**
     * @brief Initialize the FreeType font and character textures
     */
    void initialize();

    /**
     * @brief Get the character object
     *
     * @param c character
     * @return Character
     */
    Character get_character(char c);

    /**
     * @brief Get the size of a string
     *
     * @param string
     * @return glm::ivec2
     */
    glm::ivec2 get_string_size(std::string& string);
};

#endif  // GUI_TEXT_FREETYPE_FONT_H
