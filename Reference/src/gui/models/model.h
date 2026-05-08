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

#ifndef GUI_MODELS_MODEL_H
#define GUI_MODELS_MODEL_H

#include <stdexcept>

class Model {
public:
    /**
     * @brief Default constructor
     */
    Model();

    /**
     * @brief Destroy the Model object
     */
    virtual ~Model();

    /**
     * @brief Load the model to the vertex array object
     */
    virtual void load_to_vao();

    /**
     * @brief Draw the model
     */
    virtual void draw();

    /**
     * @brief Draw the model with two textures
     *
     * @param texture_a first texture color buffer to draw from
     * @param texture_b second texture color buffer to draw from
     */
    virtual void draw(unsigned int texture_a, unsigned int texture_b);

    /**
     * @brief Draw the model with three textures
     *
     * @param texture_a first texture color buffer to draw from
     * @param texture_b second texture color buffer to draw from
     * @param texture_c third texture color buffer to draw from
     */
    virtual void draw(unsigned int texture_a, unsigned int texture_b, unsigned int texture_c);
};

#endif  // GUI_MODELS_MODEL_H
