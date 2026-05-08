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

#ifndef SYMMETRY_OPERATIONS_OPERATION_MANAGER_H
#define SYMMETRY_OPERATIONS_OPERATION_MANAGER_H

#include <memory>
#include <unordered_map>
#include <vector>
#include "../../structure.h"
#include "../point_groups/point_group.h"
#include "../point_groups/point_group_label.h"
#include "operation.h"
#include "operation_group.h"
#include "operation_label.h"
#include "operation_label_count.h"

class OperationManager {
private:
    unsigned int next_id = 1;

    std::shared_ptr<Structure> structure;
    std::vector<Operation> operations;

    std::unordered_map<unsigned int, Operation> point_group_operations;
    std::vector<OperationGroup> point_group_operations_order;

public:
    /**
     * @brief Default constructor
     */
    OperationManager();

    /**
     * @brief Construct a new Operation Manager object
     *
     * @param structure
     */
    OperationManager(std::shared_ptr<Structure> structure);

    /**
     * @brief Get the list of operations present in the structure
     *
     * @return std::vector<Operation>&
     */
    std::vector<Operation>& get_operations();

    /**
     * @brief Get the list of inversion operations present in the structure
     *
     * @return const std::vector<Operation>
     */
    const std::vector<Operation> get_inversions();

    /**
     * @brief Get the list of proper rotation operations present in the
     * structure
     *
     * @return const std::vector<Operation>
     */
    const std::vector<Operation> get_proper_rotations();

    /**
     * @brief Get the list of improper rotation operations present in the
     * structure
     *
     * @return const std::vector<Operation>
     */
    const std::vector<Operation> get_improper_rotations();

    /**
     * @brief Get the list of reflection operations present in the structure
     *
     * @return const std::vector<Operation>
     */
    const std::vector<Operation> get_reflections();

    /**
     * @brief Get the map of point group operations by ID
     *
     * @return const std::unordered_map<unsigned int, Operation>&
     */
    const std::unordered_map<unsigned int, Operation>& get_point_group_operations() const;

    /**
     * @brief Get a point group operation by ID
     *
     * @return Operation&
     */
    const Operation& get_point_group_operation(unsigned int id) const;

    /**
     * @brief Get the order in which the point group operations should appear
     *
     * @return const std::vector<OperationGroup>&
     */
    const std::vector<OperationGroup>& get_point_group_operations_order() const;

    /**
     * @brief Check whether a symmetry operation exists in the structure and
     * add it to the list of operations, if it does not already exist yet
     *
     * @param operation operation to check and add
     * @return true if the operation exists (independent of whether it has
     * already been added)
     * @return false if the operation doesn't exist
     */
    bool add_operation(Operation& operation);

    /**
     * @brief Generate all operations belonging to the point group of the
     * structure, sorted by the point group order
     *
     * See generate_operations_by_label for more information.
     *
     * @param point_group
     */
    void generate_point_group_operations(PointGroup& point_group);

private:
    /**
     * @brief Check whether a symmetry operation exists in the structure
     *
     * @param operation the symmetry operation to check
     * @return true if it exists
     * @return false if it doesn't exist
     */
    bool check_operation(Operation& operation);

    /**
     * @brief Generate all operations belonging to a given operation label, and
     * return the list of IDs of these operations
     *
     * This method includes 'duplicate' operations (formed by multiplying
     * rotations). These operations are added to the unordered_map
     * point_group_operations by their ID. The order in which they should
     * appear (grouped per unique operation, as defined in
     * PointGroups::point_groups) is stored in point_group_operations_order.
     * These two objects can be obtained by their respective getters.
     *
     * @param point_group
     * @param operation_label
     */
    void generate_operations_by_label(PointGroup& point_group, OperationLabel& operation_label);

    /**
     * @brief Generate an operation group with infinite multiplicity
     *
     * Operations with infinite multiplicity (C2' and σv) occur in C∞v and D∞h
     * point groups. Due to this multiplicity, we do not search for them in the
     * operation-finding algorithm. However, we do want to show them in the
     * operation list, so we manually add them here.
     *
     * @param operation_label
     */
    void generate_infinite_operation_group(OperationLabel& operation_label);

    /**
     * @brief Copy the provided operation and give it a new ID
     *
     * @param operation operation to copy
     * @return Operation copied operation
     */
    Operation copy_operation(Operation& operation);
};

#endif  // SYMMETRY_OPERATIONS_OPERATION_MANAGER_H
