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

#include "model_2d.h"

/**
 * @brief Construct a new Model object
 *
 * @param vertices positions and texCoords of vertices
 */
Model2D::Model2D(std::vector<glm::vec4> vertices) {
    this->vertices = vertices;
}

/**
 * @brief Destroy the Model object
 */
Model2D::~Model2D() {
    if (!this->loaded_vao) return;

    this->vao.bind();
    this->vbo.destroy();
    this->vao.destroy();
}

/**
 * @brief Load the model to the vertex array object
 */
void Model2D::load_to_vao() {
    // no need to load twice
    if (this->loaded_vao) return;

    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    this->vao.create();
    this->vao.bind();

    this->vbo.create();
    this->vbo.setUsagePattern(QOpenGLBuffer::UsagePattern::StaticDraw);
    this->vbo.bind();
    this->vbo.allocate(&this->vertices[0][0], this->vertices.size() * 4 * sizeof(float));
    f->glEnableVertexAttribArray(0);
    f->glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), 0);
    f->glEnableVertexAttribArray(1);
    f->glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*) (2 * sizeof(float)));

    this->vao.release();
    this->loaded_vao = true;
}

/**
 * @brief Draw the model with two textures
 *
 * @param texture_a first texture color buffer to draw from
 * @param texture_b second texture color buffer to draw from
 */
void Model2D::draw(unsigned int texture_a, unsigned int texture_b) {
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    if (!this->loaded_vao) {
        throw std::logic_error("This model has not yet been loaded to VAO.");
    }

    this->vao.bind();
    f->glActiveTexture(GL_TEXTURE0);
    f->glBindTexture(GL_TEXTURE_2D, texture_a);
    f->glActiveTexture(GL_TEXTURE1);
    f->glBindTexture(GL_TEXTURE_2D, texture_b);
    f->glDrawArrays(GL_TRIANGLES, 0, this->vertices.size());
    this->vao.release();
}

/**
 * @brief Draw the model with three textures
 *
 * @param texture_a first texture color buffer to draw from
 * @param texture_b second texture color buffer to draw from
 * @param texture_c third texture color buffer to draw from
 */
void Model2D::draw(unsigned int texture_a, unsigned int texture_b, unsigned int texture_c) {
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    if (!this->loaded_vao) {
        throw std::logic_error("This model has not yet been loaded to VAO.");
    }

    this->vao.bind();
    f->glActiveTexture(GL_TEXTURE0);
    f->glBindTexture(GL_TEXTURE_2D, texture_a);
    f->glActiveTexture(GL_TEXTURE1);
    f->glBindTexture(GL_TEXTURE_2D, texture_b);
    f->glActiveTexture(GL_TEXTURE2);
    f->glBindTexture(GL_TEXTURE_2D, texture_c);
    f->glDrawArrays(GL_TRIANGLES, 0, this->vertices.size());
    this->vao.release();
}
