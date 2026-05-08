/**
 * Schoenflies
 * Copyright (c) 2021 Luuk Kempen
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

#ifndef GUI_MODELS_QUAD_MODEL_H
#define GUI_MODELS_QUAD_MODEL_H

#include <QOpenGLBuffer>
#include <QOpenGLContext>
#include <QOpenGLFunctions>
#include <QOpenGLVertexArrayObject>

class QuadModel {
private:
    float vertices[24] = {
        // positions   // texCoords
        -1.0f,  1.0f,  0.0f, 1.0f,
        -1.0f, -1.0f,  0.0f, 0.0f,
         1.0f, -1.0f,  1.0f, 0.0f,

        -1.0f,  1.0f,  0.0f, 1.0f,
         1.0f, -1.0f,  1.0f, 0.0f,
         1.0f,  1.0f,  1.0f, 1.0f
    };

    bool loaded_vao = false;

    QOpenGLVertexArrayObject vao;
    QOpenGLBuffer vbo;

public:
    /**
     * @brief Construct a new Quad Model object
     */
    QuadModel();

    /**
     * @brief Destroy the Quad Model object
     */
    ~QuadModel();

    /**
     * @brief Load the quad model to the vertex array object
     */
    void load_to_vao();

    /**
     * @brief Draw the quad model with two textures
     *
     * @param texture_color_buffer_a first texture color buffer to draw from
     * @param texture_color_buffer_b second texture color buffer to draw from
     */
    void draw(unsigned int texture_color_buffer_a, unsigned int texture_color_buffer_b);
};

#endif  // GUI_MODELS_QUAD_MODEL_H
