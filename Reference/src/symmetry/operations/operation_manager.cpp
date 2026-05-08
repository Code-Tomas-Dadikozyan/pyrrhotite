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

#include "operation_manager.h"

/**
 * @brief Default constructor
 */
OperationManager::OperationManager() {}

/**
 * @brief Construct a new Operation Manager object
 *
 * @param structure
 */
OperationManager::OperationManager(std::shared_ptr<Structure> structure) {
    this->structure = structure;
}

/**
 * @brief Get the list of operations present in the structure
 *
 * @return std::vector<Operation>&
 */
std::vector<Operation>& OperationManager::get_operations() {
    return this->operations;
}

/**
 * @brief Get the list of inversion operations present in the structure
 *
 * @return const std::vector<Operation>
 */
const std::vector<Operation> OperationManager::get_inversions() {
    std::vector<Operation> inversions;
    for (Operation& operation : operations) {
        if (operation.get_label().get_element() == OperationLabel::Element::Inversion)
            inversions.push_back(operation);
    }
    return inversions;
}

/**
 * @brief Get the list of proper rotation operations present in the
 * structure
 *
 * @return const std::vector<Operation>
 */
const std::vector<Operation> OperationManager::get_proper_rotations() {
    std::vector<Operation> proper_rotations;
    for (Operation& operation : operations) {
        if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation)
            proper_rotations.push_back(operation);
    }
    return proper_rotations;
}

/**
 * @brief Get the list of improper rotation operations present in the
 * structure
 *
 * @return const std::vector<Operation>
 */
const std::vector<Operation> OperationManager::get_improper_rotations() {
    std::vector<Operation> improper_rotations;
    for (Operation& operation : operations) {
        if (operation.get_label().get_element() == OperationLabel::Element::ImproperRotation)
            improper_rotations.push_back(operation);
    }
    return improper_rotations;
}

/**
 * @brief Get the list of reflection operations present in the structure
 *
 * @return const std::vector<Operation>
 */
const std::vector<Operation> OperationManager::get_reflections() {
    std::vector<Operation> reflections;
    for (Operation& operation : operations) {
        if (operation.get_label().get_element() == OperationLabel::Element::Reflection)
            reflections.push_back(operation);
    }
    return reflections;
}

/**
 * @brief Get the map of point group operations by ID
 *
 * @return const std::unordered_map<unsigned int, Operation>&
 */
const std::unordered_map<unsigned int, Operation>& OperationManager::get_point_group_operations() const {
    return this->point_group_operations;
}

/**
 * @brief Get a point group operation by ID
 *
 * @return Operation&
 */
const Operation& OperationManager::get_point_group_operation(unsigned int id) const {
    std::unordered_map<unsigned int, Operation>::const_iterator it =
        this->point_group_operations.find(id);

    if (it == this->point_group_operations.end()) {
        throw std::runtime_error("Invalid operation ID encountered: " + id);
    }

    return it->second;
}

/**
 * @brief Get the order in which the point group operations should appear
 *
 * @return const std::vector<OperationGroup>&
 */
const std::vector<OperationGroup>& OperationManager::get_point_group_operations_order() const {
    return this->point_group_operations_order;
}

/**
 * @brief Check whether a symmetry operation exists in the structure and
 * add it to the list of operations, if it does not already exist yet
 *
 * @param operation operation to check and add
 * @return true if the operation exists (independent of whether it has
 * already been added)
 * @return false if the operation doesn't exist
 */
bool OperationManager::add_operation(Operation& operation) {
    bool operation_exists = this->check_operation(operation);

    if (operation_exists) {
        bool found = false;

        operation.set_id(this->next_id++);

        for (unsigned int i = 0; i < this->operations.size(); ++i) {
            if (operation == this->operations[i]) {
                if (operation.get_error() < this->operations[i].get_error()) {
                    this->operations[i] = operation;
                }

                found = true;
                break;
            }
        }

        if (!found) this->operations.push_back(operation);
    }

    return operation_exists;
}

/**
 * @brief Check whether a symmetry operation exists in the structure
 *
 * @param operation the symmetry operation to check
 * @return true if it exists
 * @return false if it doesn't exist
 */
bool OperationManager::check_operation(Operation& operation) {
    operation.do_operation(this->structure);

    // TODO move tolerance to a variable/constant
    return operation.get_error() < .1;
}

/**
 * @brief Generate all operations belonging to the point group of the
 * structure, sorted by the point group order
 *
 * See generate_operations_by_label for more information.
 *
 * @param point_group
 */
void OperationManager::generate_point_group_operations(PointGroup& point_group) {
    std::vector<OperationLabelCount> operation_labels = point_group.get_unique_operations();

    for (OperationLabelCount& operation_label : operation_labels) {
        this->generate_operations_by_label(point_group, operation_label.get_label());
    }
}

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
void OperationManager::generate_operations_by_label(PointGroup& point_group, OperationLabel& operation_label) {
    // handle special cases (∞ C2' and ∞ σv in C∞v, D∞h)
    if ((point_group.get_label().get_class() == PointGroupLabel::Class::Cinfv ||
         point_group.get_label().get_class() == PointGroupLabel::Class::Dinfh) &&
        (operation_label.get_element() == OperationLabel::Element::ProperRotation &&
         operation_label.get_degree() == 2 ||
         operation_label.get_element() == OperationLabel::Element::Reflection)) {
        this->generate_infinite_operation_group(operation_label);
        return;
    }

    OperationGroup operation_group(operation_label);

    // find operations with matching label
    std::vector<Operation> matches;
    for (Operation& operation : this->operations) {
        if (operation.get_label().matches(operation_label)) {
            matches.push_back(operation);
        }
    }

    if (operation_label.get_element() == OperationLabel::Element::Inversion ||
        operation_label.get_element() == OperationLabel::Element::Reflection) {
        // inversion and reflection can be added directly
        for (Operation& match : matches) {
            point_group_operations.insert({match.get_id(), match});
            operation_group.add_operation_id(match.get_id());
        }
    } else {
        // (im)proper rotations need multiples
        std::vector<int> multiples;
        if (operation_label.get_degree() > 2) {
            multiples = {operation_label.get_multiple(), -operation_label.get_multiple()};
        } else {
            multiples = {operation_label.get_multiple()};
        }

        for (int& multiple : multiples) {
            for (Operation& match : matches) {
                if (multiple == match.get_label().get_multiple()) {
                    // re-use already-created operation
                    point_group_operations.insert({match.get_id(), match});
                    operation_group.add_operation_id(match.get_id());
                } else {
                    // copy operation, set multiple, and add new id
                    Operation copy = this->copy_operation(match);
                    copy.get_label().set_multiple(multiple);
                    point_group_operations.insert({copy.get_id(), copy});
                    operation_group.add_operation_id(copy.get_id());
                }
            }
        }
    }

    this->point_group_operations_order.push_back(operation_group);
}

/**
 * @brief Generate an operation with infinite multiplicity
 *
 * These operations (C2' and σv) occur in C∞v and D∞h point groups. Due to
 * their infinite multiplicity, we do not search for them in the operation-
 * finding algorithm. However, we do want to show them in the operation
 * list, so we manually add them here.
 *
 * @param operation_label
 */
void OperationManager::generate_infinite_operation_group(OperationLabel& operation_label) {
    OperationGroup operation_group(operation_label);
    operation_group.set_infinite_multiplicity(true);

    this->point_group_operations_order.push_back(operation_group);
}

/**
 * @brief Copy the provided operation and give it a new ID
 *
 * @param operation operation to copy
 * @return Operation copied operation
 */
Operation OperationManager::copy_operation(Operation& operation) {
    Operation copy = operation;
    copy.set_id(this->next_id++);
    return copy;
}
