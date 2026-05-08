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

#include "model_manager.h"

/**
 * @brief Construct a new Model Manager object
 */
ModelManager::ModelManager() {}

/**
 * @brief Get pointer to a model
 *
 * @param name name of the model
 * @return Model* pointer to model
 */
Model* ModelManager::get_model(const std::string& name) {
    auto it = this->model_map.find(name);

    if (it == this->model_map.end()) {
        throw std::logic_error("Invalid model encountered: " + name);
    }

    return it->second.get();
}

/**
 * @brief Add a new model
 *
 * @param name model name
 * @param model model object
 */
void ModelManager::add_model(const std::string& name, std::unique_ptr<Model> model) {
    this->model_map.emplace(name, std::move(model));
}

/**
 * @brief Load all models to their vertex array objects
 */
void ModelManager::load_models_to_vao() {
    for (auto& model : this->model_map) {
        model.second->load_to_vao();
    }
}
