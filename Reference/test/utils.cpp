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

#include "utils.h"

/**
 * @brief Resolve a relative path by recursively moving up the directory tree.
 * This finds full paths as long as the working directory in which the test
 * script is executed is a descendant of the project's root directory.
 *
 * From https://stackoverflow.com/a/42772814
 *
 * @param relative_path relative path to search for
 * @return std::string absolute path
 */
std::string resolve_path(const std::string &relative_path) {
    auto base_dir = boost::filesystem::current_path();
    while (base_dir.has_parent_path()) {
        auto combine_path = base_dir / relative_path;
        if (boost::filesystem::exists(combine_path)) {
            return combine_path.string();
        }
        base_dir = base_dir.parent_path();
    }
    throw std::runtime_error("Could not find file: " + relative_path);
}
