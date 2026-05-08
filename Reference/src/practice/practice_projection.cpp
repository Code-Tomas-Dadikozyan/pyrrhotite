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

#include "practice_projection.h"

/**
 * @brief Default constructor
 */
PracticeProjection::PracticeProjection() {}

/**
 * @brief Construct a new Practice Projection object
 *
 * @param practice_structure practice structure object
 */
PracticeProjection::PracticeProjection(std::shared_ptr<PracticeStructure> practice_structure) {
    this->practice_structure = practice_structure;
    this->calculate_coefficients();
}

/**
 * @brief Get the correct coefficient values
 *
 * @return std::vector<std::pair<OperationLabelCount, std::vector<double>>>&
 */
std::vector<std::pair<OperationLabelCount, std::vector<double>>>& PracticeProjection::get_correct_coefficients() {
    return this->correct_coefficients;
}

/**
 * @brief Calculate the coefficient of each operation
 */
void PracticeProjection::calculate_coefficients() {
    std::shared_ptr<Symmetry> symmetry = this->practice_structure->get_symmetry();
    std::shared_ptr<BasisSet> basis_set = this->practice_structure->get_basis_set();
    unsigned int base_atom = this->practice_structure->get_base_atom();
    unsigned int base_atom_index = basis_set->get_atoms()[base_atom];

    std::vector<OperationLabelCount> operation_labels_count = symmetry->get_point_group().get_unique_operations();
    std::unordered_map<unsigned int, Operation> operations = symmetry->get_operation_manager()->get_point_group_operations();

    for (auto& operation_label_count : operation_labels_count) {
        // find the operations with this label
        unsigned int num_operations_found = 0;

        std::vector<double> coefficients(basis_set->get_atoms().size());

        for (auto& point_group_operation : operations) {
            Operation& operation = point_group_operation.second;

            if (!operation.get_label().matches_strict(operation_label_count.get_label())) continue;
            num_operations_found++;

            // determine the transformation
            unsigned int result_index = operation.get_result_index(base_atom_index);  // always in basis set
            auto bs_it = std::find(basis_set->get_atoms().begin(), basis_set->get_atoms().end(), result_index);
            if (bs_it == basis_set->get_atoms().end()) {
                throw std::runtime_error("Resulting index not in basis set, this should not happen");
            }
            unsigned int bs_index = std::distance(basis_set->get_atoms().begin(), bs_it);

            if (basis_set->get_orbital_label().get_azimuthal() == 0) {  // s
                coefficients[bs_index]++;
            } else {  // p
                coefficients[bs_index] += glm::dot(operation.do_atom_operation(basis_set->get_orbital_vector()),
                                                   basis_set->get_orbital_vector());
            }
        }

        if (num_operations_found != operation_label_count.get_count()) {
            throw std::runtime_error("Incorrect number of operations found, this should not happen");
        }

        this->correct_coefficients.push_back(std::make_pair(operation_label_count, coefficients));
    }
}
