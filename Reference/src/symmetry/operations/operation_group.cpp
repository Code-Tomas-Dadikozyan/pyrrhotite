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

#include "operation_group.h"

/**
 * @brief Construct a new Operation Group object
 *
 * @param operation_label
 */
OperationGroup::OperationGroup(OperationLabel& operation_label) {
    this->operation_label = operation_label;
}

/**
 * @brief Get the point group operation IDs
 *
 * @return std::vector<unsigned int>&
 */
const std::vector<unsigned int>& OperationGroup::get_operation_ids() const {
    return this->operation_ids;
}

/**
 * @brief Get whether the operation group has infinite multiplicity
 *
 * @return true
 * @return false
 */
const bool OperationGroup::get_infinite_multiplicity() const {
    return this->infinite_multiplicity;
}

/**
 * @brief Add point group operation to the operation group by ID
 *
 * @param id point group operation ID
 */
void OperationGroup::add_operation_id(const unsigned int id) {
    this->operation_ids.push_back(id);
}

/**
 * @brief Set whether the operation group has infinite multiplicity
 *
 * @param infinite_multiplicity
 */
void OperationGroup::set_infinite_multiplicity(bool infinite_multiplicity) {
    this->infinite_multiplicity = infinite_multiplicity;
}

/**
 * @brief Get the number of operations in this group
 *
 * @return const unsigned int
 */
const unsigned int OperationGroup::get_num_operations() const {
    return this->operation_ids.size();
}

/**
 * @brief Get the name of this operation group in plaintext
 *
 * @return const std::string
 */
const std::string OperationGroup::get_name() const {
    std::string name = this->operation_label.get_name();

    if (this->operation_ids.size() > 1 || this->infinite_multiplicity) {
        name += "s (";
        name += (this->infinite_multiplicity) ? "∞" : std::to_string(this->operation_ids.size());
        name += ")";
    }

    return name;
}

/**
 * @brief Get the name of this operation group in HTML formatting
 *
 * @return const std::string
 */
const std::string OperationGroup::get_name_html() const {
    std::string name = this->operation_label.get_name_html();

    if (this->operation_ids.size() > 1 || this->infinite_multiplicity) {
        name += "s (";
        name += (this->infinite_multiplicity) ? "∞" : std::to_string(this->operation_ids.size());
        name += ")";
    }

    return name;
}
