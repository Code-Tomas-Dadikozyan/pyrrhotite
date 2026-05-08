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

#include "model.h"

/**
 * @brief Default constructor
 */
Model::Model() {}

/**
 * @brief Destroy the Model object
 */
Model::~Model() {}

/**
 * @brief Load the model to the vertex array object
 */
void Model::load_to_vao() {
    throw std::logic_error("Do not call methods from the base Model class!");
}

/**
 * @brief Draw the model
 */
void Model::draw() {
    throw std::logic_error("Do not call methods from the base Model class!");
}

/**
 * @brief Draw the model with two textures
 *
 * @param texture_a first texture color buffer to draw from
 * @param texture_b second texture color buffer to draw from
 */
void Model::draw(unsigned int texture_a, unsigned int texture_b) {
    throw std::logic_error("Do not call methods from the base Model class!");
}

/**
 * @brief Draw the model with three textures
 *
 * @param texture_a first texture color buffer to draw from
 * @param texture_b second texture color buffer to draw from
 * @param texture_c third texture color buffer to draw from
 */
void Model::draw(unsigned int texture_a, unsigned int texture_b, unsigned int texture_c) {
    throw std::logic_error("Do not call methods from the base Model class!");
}
