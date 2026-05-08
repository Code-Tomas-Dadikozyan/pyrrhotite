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

#ifndef PRACTICE_PRACTICE_PROJECTION_H
#define PRACTICE_PRACTICE_PROJECTION_H

#include <memory>
#include <unordered_map>
#include <utility>
#include <vector>
#include "../symmetry/operations/operation.h"
#include "../symmetry/operations/operation_label_count.h"
#include "../symmetry/symmetry.h"
#include "../basis_set.h"
#include "practice_structure.h"

class PracticeProjection {
private:
    std::shared_ptr<PracticeStructure> practice_structure;

    std::vector<std::pair<OperationLabelCount, std::vector<double>>> correct_coefficients;

public:
    /**
     * @brief Default constructor
     */
    PracticeProjection();

    /**
     * @brief Construct a new Practice Projection object
     *
     * @param practice_structure practice structure object
     */
    PracticeProjection(std::shared_ptr<PracticeStructure> practice_structure);

    /**
     * @brief Get the correct coefficient values
     *
     * @return std::vector<std::pair<OperationLabelCount, std::vector<double>>>&
     */
    std::vector<std::pair<OperationLabelCount, std::vector<double>>>& get_correct_coefficients();

private:
    /**
     * @brief Calculate the coefficient of each operation
     */
    void calculate_coefficients();
};

#endif  // PRACTICE_PRACTICE_PROJECTION_H
