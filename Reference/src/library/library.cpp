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

#include "library.h"

/**
 * @brief Construct a new Library object
 *
 * @param include_built_in_library whether to immediately load the library
 * built in to this program. Only set this to `false` for testing purposes!
 */
Library::Library(bool include_built_in_library) {
    if (include_built_in_library) this->add_items_from_package(":/assets/structures/library.json");

    std::random_device device;
    this->random_engine = std::mt19937(device());
}

/**
 * @brief Get the items in the library
 *
 * @return std::vector<LibraryItem>&
 */
std::vector<LibraryItem>& Library::get_items() {
    if (!this->items_sorted) {
        std::sort(this->items.begin(), this->items.end());
        if (this->practice_subset_generated) this->generate_practice_subset();  // regenerate due to sorting
        this->items_sorted = true;
    }

    return this->items;
}

/**
 * @brief Get a random practice item from the library
 *
 * @return LibraryItem&
 */
LibraryItem& Library::get_practice_item() {
    LibraryItem& item = this->items[this->practice_subset[this->practice_subset_index++]];
    if (this->practice_subset_index >= this->practice_subset.size()) this->practice_subset_index = 0;
    return item;
}

/**
 * @brief Set the practice config object
 *
 * @param practice_config
 */
void Library::set_practice_config(const std::shared_ptr<PracticeConfig> practice_config) {
    this->practice_config = practice_config;
    this->generate_practice_subset();
}

/**
 * @brief Add items from a package
 *
 * @param path path to the package metadata file
 */
void Library::add_items_from_package(const std::string path) {
    LibraryPackage package(path);

    for (unsigned int i = 0; i < package.get_size(); ++i) {
        this->items.push_back(package.get_item(i));
    }

    this->items_sorted = false;
}

/**
 * @brief Generate the subset of library items available for practice
 */
void Library::generate_practice_subset() {
    this->practice_subset.clear();
    for (unsigned int i = 0; i < this->items.size(); ++i) {
        if (this->items[i].can_appear_in_practice(practice_config)) {
            this->practice_subset.push_back(i);
        }
    }
    std::shuffle(this->practice_subset.begin(), this->practice_subset.end(), this->random_engine);
    this->practice_subset_index = 0;
    this->practice_subset_generated = true;
}
