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

#ifndef PRACTICE_PRACTICE_MODULES_H
#define PRACTICE_PRACTICE_MODULES_H

#include <stdexcept>
#include <string>
#include <unordered_map>
#include "practice_module.h"

class PracticeModules final {
private:
    /**
     * @brief Mapping from practice module enum to string key
     */
    static const std::unordered_map<PracticeModule, std::string> keys;

public:
    /**
     * @brief Get the string key from a practice module enum
     *
     * @param practice_module practice module enum
     * @return std::string
     */
    static std::string get_key(const PracticeModule practice_module);

private:
    /**
     * @brief Default constructor
     */
    PracticeModules() {}
};

#endif  // PRACTICE_PRACTICE_MODULES_H
