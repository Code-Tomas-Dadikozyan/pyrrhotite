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

#ifndef GUI_MODELS_MODEL_3D_H
#define GUI_MODELS_MODEL_3D_H

#include <vector>
#include <glm/glm.hpp>
#include <QOpenGLBuffer>
#include <QOpenGLContext>
#include <QOpenGLFunctions>
#include <QOpenGLVertexArrayObject>
#include "model.h"

class Model3D: public Model {
private:
    std::vector<glm::vec3> positions;
    std::vector<glm::vec3> normals;
    std::vector<unsigned int> indices;

    bool loaded_vao = false;

    QOpenGLVertexArrayObject vao;
    QOpenGLBuffer vbo[3];

public:
    /**
     * @brief Construct a new Model object
     *
     * @param positions positions of vertices
     * @param normals normals of vertices
     * @param indices triples of vertices forming triangles
     */
    Model3D(std::vector<glm::vec3> positions, std::vector<glm::vec3> normals, std::vector<unsigned int> indices);

    /**
     * @brief Destroy the Model object
     */
    ~Model3D() override;

    /**
     * @brief Load the model to the vertex array object
     */
    void load_to_vao() override;

    /**
     * @brief Draw the model
     */
    void draw() override;
};

#endif  // GUI_MODELS_MODEL_3D_H
