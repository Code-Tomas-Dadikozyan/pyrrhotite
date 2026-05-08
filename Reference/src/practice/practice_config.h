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

#ifndef PRACTICE_PRACTICE_CONFIG_H
#define PRACTICE_PRACTICE_CONFIG_H

#include <algorithm>
#include <stdexcept>
#include <vector>
#include "practice_module.h"

class PracticeConfig {
private:
    std::vector<PracticeModule> enabled_modules;
    int current_module_index = -1;
    bool select_new_structure;

public:
    /**
     * @brief Construct a new PracticeConfig object
     */
    PracticeConfig();

    /**
     * @brief Add a practice module if it hasn't been added already
     *
     * @param module module to add
     */
    void add_module(PracticeModule module);

    /**
     * @brief Get the list of enabled practice modules
     *
     * @return const std::vector<PracticeModule>
     */
    const std::vector<PracticeModule> get_enabled_modules() const;

    /**
     * @brief Get the next practice module to use and advance the internal
     * counter
     *
     * @return PracticeModule
     */
    PracticeModule get_next_module();

    /**
     * @brief Get the flag that indicates whether a new structure should be
     * selected
     *
     * @return true
     * @return false
     */
    bool get_select_new_structure();
};

#endif  // PRACTICE_PRACTICE_CONFIG_H
