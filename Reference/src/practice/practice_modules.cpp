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

#include "practice_modules.h"

/**
 * @brief Mapping from practice module enum to string key
 */
const std::unordered_map<PracticeModule, std::string> PracticeModules::keys = {
    {PracticeModule::Flowchart, "flowchart"},
    {PracticeModule::Irreps, "irreps"},
    {PracticeModule::Projection, "projection"}
};

/**
 * @brief Get the string key from a practice module enum
 *
 * @param practice_module practice module enum
 * @return std::string
 */
std::string PracticeModules::get_key(const PracticeModule practice_module) {
    std::unordered_map<PracticeModule, std::string>::const_iterator it =
        PracticeModules::keys.find(practice_module);

    if (it == PracticeModules::keys.end()) {
        throw std::runtime_error("Invalid practice module encountered.");
    }

    return it->second;
}
