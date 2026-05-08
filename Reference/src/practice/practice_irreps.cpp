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

#include "practice_irreps.h"

/**
 * @brief Default constructor
 */
PracticeIrreps::PracticeIrreps() {}

/**
 * @brief Construct a new Practice Irreps object
 *
 * @param practice_structure practice structure object
 */
PracticeIrreps::PracticeIrreps(std::shared_ptr<PracticeStructure> practice_structure) {
    this->practice_structure = practice_structure;
    this->calculate();
}

/**
 * @brief Get the correct character values
 *
 * @return std::vector<std::pair<OperationLabelCount, double>>&
 */
std::vector<std::pair<OperationLabelCount, double>>& PracticeIrreps::get_correct_characters() {
    return this->correct_characters;
}

/**
 * @brief Get the correct irrep values
 *
 * @return std::vector<std::pair<IrrepLabel, double>>
 */
std::vector<std::pair<IrrepLabel, double>> PracticeIrreps::get_correct_irreps() {
    return this->correct_irreps;
}

/**
 * @brief Calculate the correct answers to the questions
 */
void PracticeIrreps::calculate() {
    this->calculate_characters();
    this->calculate_irreps();
}

/**
 * @brief Calculate the character of each operation (how many orbitals
 * remain in place)
 */
void PracticeIrreps::calculate_characters() {
    std::shared_ptr<Symmetry> symmetry = this->practice_structure->get_symmetry();
    std::shared_ptr<BasisSet> basis_set = this->practice_structure->get_basis_set();

    std::vector<OperationLabelCount> operation_labels_count = symmetry->get_point_group().get_unique_operations();
    std::vector<Operation> operations = symmetry->get_operation_manager()->get_operations();

    for (auto& operation_label_count : operation_labels_count) {
        // find an operation with this label
        unsigned int operation_index;
        bool found = false;

        for (unsigned int i = 0; i < operations.size(); ++i) {
            if (operations[i].get_label().matches(operation_label_count.get_label())) {
                operation_index = i;
                found = true;
                break;
            }
        }

        if (!found) {
            throw std::runtime_error("Could not find an operation, this should not happen");
        }

        Operation& operation = operations[operation_index];

        // determine the character of this operation
        double character = 0;
        for (unsigned int index : basis_set->get_atoms()) {
            if (operation.get_result_index(index) == index) {
                if (basis_set->get_orbital_label().get_azimuthal() == 0) {  // s
                    character++;
                } else {  // p
                    character += glm::dot(operation.do_atom_operation(basis_set->get_orbital_vector()),
                                          basis_set->get_orbital_vector());
                }
            }
        }
        character *= operation_label_count.get_count();  // multiply by number of operations

        this->correct_characters.push_back(std::make_pair(operation_label_count, character));
    }
}

/**
 * @brief Calculate the irreducible representations of the structure
 */
void PracticeIrreps::calculate_irreps() {
    std::shared_ptr<Symmetry> symmetry = this->practice_structure->get_symmetry();
    std::shared_ptr<BasisSet> basis_set = this->practice_structure->get_basis_set();

    std::vector<int> character_coefficients;
    character_coefficients.push_back(basis_set->get_atoms().size());  // manually add identity
    for (auto character : correct_characters) {
        character_coefficients.push_back(character.second);
    }

    std::vector<IrrepLabel> irreps = symmetry->get_point_group().get_irreps();
    std::vector<std::vector<double>> characters = symmetry->get_point_group().get_characters();
    unsigned int order = symmetry->get_point_group().get_order();

    for (unsigned int i = 0; i < irreps.size(); ++i) {
        if (character_coefficients.size() != characters[i].size()) {
            throw std::runtime_error("Vector sizes have to be equal to calculate irreps");
        }
        double dot = 0;
        for (unsigned int j = 0; j < character_coefficients.size(); ++j) {
            dot += character_coefficients[j] * characters[i][j];
        }

        this->correct_irreps.push_back(std::make_pair(irreps[i], dot / order));
    }
}
