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

#include "point_group.h"

/**
 * @brief Default constructor
 */
PointGroup::PointGroup() {}

/**
 * @brief Construct a new Point Group object
 *
 * Note that, for the number of rotations, degenerate rotations (rotations
 * with the same degree around the same axis, e.g. C_3 and C_3^2) are only
 * counted once.
 *
 * @param label point group label
 * @param order order of this point group (total number of unique symmetry operations)
 * @param num_inversions number of inversions in this point group
 * @param num_proper_rotations number of proper rotations per degree in this point group
 * @param num_improper_rotations number of improper rotations per degree in this point group
 * @param num_reflections number of reflections in this point group
 * @param unique_operations vector of labels of unique operations in this point group
 * @param irreps vector of irreducible representations in this point group
 * @param characters matrix of characters (indexed as [irrep][operation])
 */
PointGroup::PointGroup(
    PointGroupLabel label,
    unsigned int order,
    unsigned int num_inversions,
    std::unordered_map<unsigned int, unsigned int> num_proper_rotations,
    std::unordered_map<unsigned int, unsigned int> num_improper_rotations,
    unsigned int num_reflections,
    std::vector<OperationLabelCount> unique_operations,
    std::vector<IrrepLabel> irreps,
    std::vector<std::vector<double>> characters
) {
    this->label = label;
    this->order = order;
    this->num_inversions = num_inversions;
    this->num_proper_rotations = num_proper_rotations;
    this->num_improper_rotations = num_improper_rotations;
    this->num_reflections = num_reflections;
    this->unique_operations = unique_operations;
    this->irreps = irreps;
    this->characters = characters;
}

/**
 * @brief Compare this point group to a list of found symmetry operations
 *
 * @param inversions list of found inversions
 * @param proper_rotations list of found proper rotations
 * @param improper_rotations list of found improper rotations
 * @param reflections list of found reflections
 * @return const int -1 if not all symmetry operations in this point group
 * were found, or a positive number indicating the number of symmetry
 * operations found but not in the point group
 */
const unsigned int PointGroup::compare_to_symmetry_operations(std::vector<Operation>& operations) const {
    // initialise num_remaining as total of all operations
    // we then subtract all operations that were found in the point group
    unsigned int num_remaining = operations.size();

    // first, check inversions and reflections, as these do not have degrees
    unsigned int num_inversions = 0, num_reflections = 0;
    for (unsigned int i = 0; i < operations.size(); ++i) {
        OperationLabel::Element element = operations[i].get_label().get_element();

        if (element == OperationLabel::Element::Inversion) num_inversions++;
        if (element == OperationLabel::Element::Reflection) num_reflections++;
    }

    if (num_inversions < this->num_inversions) return -1;
    num_remaining -= this->num_inversions;

    if (num_reflections < this->num_reflections) return -1;
    num_remaining -= this->num_reflections;

    // then, check rotations
    for (auto& num_proper_rotation : this->num_proper_rotations) {
        unsigned int degree = num_proper_rotation.first;
        unsigned int num = num_proper_rotation.second;

        unsigned int num_found = 0;
        for (unsigned int i = 0; i < operations.size(); ++i) {
            if (operations[i].get_label().get_element() != OperationLabel::Element::ProperRotation) continue;
            if (operations[i].get_degree() == degree) num_found++;
        }

        if (num_found < num) return -1;
        num_remaining -= num;
    }

    for (auto& num_improper_rotation : this->num_improper_rotations) {
        unsigned int degree = num_improper_rotation.first;
        unsigned int num = num_improper_rotation.second;

        unsigned int num_found = 0;
        for (unsigned int i = 0; i < operations.size(); ++i) {
            if (operations[i].get_label().get_element() != OperationLabel::Element::ImproperRotation) continue;
            if (operations[i].get_degree() == degree) num_found++;
        }

        if (num_found < num) return -1;
        num_remaining -= num;
    }

    return num_remaining;
}

/**
 * @brief Get the label of the point group
 *
 * @return const PointGroupLabel&
 */
const PointGroupLabel& PointGroup::get_label() const {
    return this->label;
}

/**
 * @brief Get the order of the point group
 *
 * @return const unsigned int
 */
const unsigned int PointGroup::get_order() const {
    return this->order;
}

/**
 * @brief Get the unique operations of the point group
 *
 * @return const std::vector<OperationLabelCount>&
 */
const std::vector<OperationLabelCount>& PointGroup::get_unique_operations() const {
    return this->unique_operations;
}

/**
 * @brief Get the irreducible representations of the point group
 *
 * @return const std::vector<IrrepLabel>&
 */
const std::vector<IrrepLabel>& PointGroup::get_irreps() const {
    return this->irreps;
}

/**
 * @brief Get the characters matrix of the point group
 *
 * @return const std::vector<std::vector<double>>&
 */
const std::vector<std::vector<double>>& PointGroup::get_characters() const {
    return this->characters;
}
