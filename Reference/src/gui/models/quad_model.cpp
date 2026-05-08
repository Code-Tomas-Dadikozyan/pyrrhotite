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

#include "quad_model.h"

/**
 * @brief Construct a new Quad Model object
 */
QuadModel::QuadModel() {}

/**
 * @brief Destroy the Quad Model object
 */
QuadModel::~QuadModel() {
    if (!this->loaded_vao) return;

    this->vao.bind();
    this->vbo.destroy();
    this->vao.destroy();
}

/**
 * @brief Load the quad model to the vertex array object
 */
void QuadModel::load_to_vao() {
    // no need to load twice
    if (this->loaded_vao) return;

    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    this->vao.create();
    this->vao.bind();

    this->vbo.create();
    this->vbo.setUsagePattern(QOpenGLBuffer::UsagePattern::StaticDraw);
    this->vbo.bind();
    this->vbo.allocate(this->vertices, sizeof(this->vertices));
    f->glEnableVertexAttribArray(0);
    f->glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), 0);
    f->glEnableVertexAttribArray(1);
    f->glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*) (2 * sizeof(float)));

    this->vao.release();
    this->loaded_vao = true;
}

/**
 * @brief Draw the quad model with two textures
 *
 * @param texture_color_buffer_a first texture color buffer to draw from
 * @param texture_color_buffer_b second texture color buffer to draw from
 */
void QuadModel::draw(unsigned int texture_color_buffer_a, unsigned int texture_color_buffer_b) {
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    this->vao.bind();
    f->glActiveTexture(GL_TEXTURE0);
    f->glBindTexture(GL_TEXTURE_2D, texture_color_buffer_a);
    f->glActiveTexture(GL_TEXTURE1);
    f->glBindTexture(GL_TEXTURE_2D, texture_color_buffer_b);
    f->glDrawArrays(GL_TRIANGLES, 0, 6);
    this->vao.release();
}
