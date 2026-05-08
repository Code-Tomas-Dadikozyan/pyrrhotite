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

#ifndef GUI_MODELS_MODEL_2D_H
#define GUI_MODELS_MODEL_2D_H

#include <vector>
#include <glm/glm.hpp>
#include <QOpenGLBuffer>
#include <QOpenGLContext>
#include <QOpenGLFunctions>
#include <QOpenGLVertexArrayObject>
#include "model.h"

class Model2D: public Model {
private:
    std::vector<glm::vec4> vertices;

    bool loaded_vao = false;

    QOpenGLVertexArrayObject vao;
    QOpenGLBuffer vbo;

public:
    /**
     * @brief Construct a new Model object
     *
     * @param vertices positions and texCoords of vertices
     */
    Model2D(std::vector<glm::vec4> vertices);

    /**
     * @brief Destroy the Model object
     */
    ~Model2D() override;

    /**
     * @brief Load the model to the vertex array object
     */
    void load_to_vao() override;

    /**
     * @brief Draw the model with two textures
     *
     * @param texture_a first texture color buffer to draw from
     * @param texture_b second texture color buffer to draw from
     */
    void draw(unsigned int texture_a, unsigned int texture_b) override;

    /**
     * @brief Draw the model with three textures
     *
     * @param texture_a first texture color buffer to draw from
     * @param texture_b second texture color buffer to draw from
     * @param texture_c third texture color buffer to draw from
     */
    void draw(unsigned int texture_a, unsigned int texture_b, unsigned int texture_c) override;
};

#endif  // GUI_MODELS_MODEL_2D_H
