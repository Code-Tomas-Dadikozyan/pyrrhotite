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

#ifndef SYMMETRY_OPERATIONS_OPERATION_GROUP_H
#define SYMMETRY_OPERATIONS_OPERATION_GROUP_H

#include <string>
#include <vector>
#include "operation_label.h"

class OperationGroup {
private:
    OperationLabel operation_label;
    std::vector<unsigned int> operation_ids;
    bool infinite_multiplicity = false;

public:
    /**
     * @brief Construct a new Operation Group object
     *
     * @param operation_label
     */
    OperationGroup(OperationLabel& operation_label);

    /**
     * @brief Get the point group operation IDs
     *
     * @return const std::vector<unsigned int>&
     */
    const std::vector<unsigned int>& get_operation_ids() const;

    /**
     * @brief Get whether the operation group has infinite multiplicity
     *
     * @return true
     * @return false
     */
    const bool get_infinite_multiplicity() const;

    /**
     * @brief Add point group operation to the operation group by ID
     *
     * @param id point group operation ID
     */
    void add_operation_id(const unsigned int id);

    /**
     * @brief Set whether the operation group has infinite multiplicity
     *
     * @param infinite_multiplicity
     */
    void set_infinite_multiplicity(bool infinite_multiplicity);

    /**
     * @brief Get the number of operations in this group
     *
     * @return const unsigned int
     */
    const unsigned int get_num_operations() const;

    /**
     * @brief Get the name of this operation group in plaintext
     *
     * @return const std::string
     */
    const std::string get_name() const;

    /**
     * @brief Get the name of this operation group in HTML formatting
     *
     * @return const std::string
     */
    const std::string get_name_html() const;
};

#endif  // SYMMETRY_OPERATIONS_OPERATION_GROUP_H
