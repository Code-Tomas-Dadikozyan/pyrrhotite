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

#include "practice_config.h"

/**
 * @brief Construct a new PracticeConfig object
 */
PracticeConfig::PracticeConfig() {}

/**
 * @brief Add a practice module if it hasn't been added already
 *
 * @param module module to add
 */
void PracticeConfig::add_module(PracticeModule module) {
    if (std::find(this->enabled_modules.begin(), this->enabled_modules.end(), module) !=
        this->enabled_modules.end()) return;

    this->enabled_modules.push_back(module);
}

/**
 * @brief Get the list of enabled practice modules
 *
 * @return const std::vector<PracticeModule>
 */
const std::vector<PracticeModule> PracticeConfig::get_enabled_modules() const {
    return this->enabled_modules;
}

/**
 * @brief Get the next practice module to use and advance the internal
 * counter
 *
 * @return PracticeModule
 */
PracticeModule PracticeConfig::get_next_module() {
    if (this->enabled_modules.size() == 0) {
        throw std::runtime_error("Tried to get a practice module when none are enabled.");
    }

    this->current_module_index++;
    if (this->current_module_index >= this->enabled_modules.size()) this->current_module_index = 0;

    this->select_new_structure = (this->current_module_index == 0);

    return this->enabled_modules[this->current_module_index];
}

/**
 * @brief Get the flag that indicates whether a new structure should be
 * selected
 *
 * @return true
 * @return false
 */
bool PracticeConfig::get_select_new_structure() {
    return this->select_new_structure;
}
