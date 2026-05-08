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

#include "model_3d.h"

/**
 * @brief Construct a new Model object
 *
 * @param positions positions of vertices
 * @param normals normals of vertices
 * @param indices triples of vertices forming triangles
 */
Model3D::Model3D(std::vector<glm::vec3> positions, std::vector<glm::vec3> normals, std::vector<unsigned int> indices) {
    this->positions = positions;
    this->normals = normals;
    this->indices = indices;
}

/**
 * @brief Destroy the Model object
 */
Model3D::~Model3D() {
    if (!this->loaded_vao) return;

    this->vao.bind();
    for (unsigned int i = 0; i < 3; ++i) {
        this->vbo[i].destroy();
    }
    this->vao.destroy();
}

/**
 * @brief Load the model to the vertex array object
 */
void Model3D::load_to_vao() {
    // no need to load twice
    if (this->loaded_vao) return;

    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    this->vao.create();
    this->vao.bind();

    this->vbo[0].create();
    this->vbo[0].setUsagePattern(QOpenGLBuffer::UsagePattern::StaticDraw);
    this->vbo[0].bind();
    this->vbo[0].allocate(&this->positions[0][0], this->positions.size() * 3 * sizeof(float));
    f->glEnableVertexAttribArray(0);
    f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0);

    this->vbo[1].create();
    this->vbo[1].setUsagePattern(QOpenGLBuffer::UsagePattern::StaticDraw);
    this->vbo[1].bind();
    this->vbo[1].allocate(&this->normals[0][0], this->normals.size() * 3 * sizeof(float));
    f->glEnableVertexAttribArray(1);
    f->glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, 0);

    this->vbo[2] = QOpenGLBuffer(QOpenGLBuffer::Type::IndexBuffer);
    this->vbo[2].create();
    this->vbo[2].setUsagePattern(QOpenGLBuffer::UsagePattern::StaticDraw);
    this->vbo[2].bind();
    this->vbo[2].allocate(&this->indices[0], this->indices.size() * sizeof(unsigned int));

    this->vao.release();
    this->loaded_vao = true;
}

/**
 * @brief Draw this model
 */
void Model3D::draw() {
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    if (!this->loaded_vao) {
        throw std::logic_error("This model has not yet been loaded to VAO.");
    }

    this->vao.bind();
    f->glDrawElements(GL_TRIANGLES, this->indices.size(), GL_UNSIGNED_INT, 0);
    this->vao.release();
}
