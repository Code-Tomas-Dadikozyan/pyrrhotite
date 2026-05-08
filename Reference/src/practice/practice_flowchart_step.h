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

#ifndef PRACTICE_PRACTICE_FLOWCHART_STEP_H
#define PRACTICE_PRACTICE_FLOWCHART_STEP_H

#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include "../symmetry/symmetry.h"
#include "../symmetry/point_groups/point_group_label.h"

class PracticeFlowchartStep {
public:
    enum Type {
        NoYes,
        ChooseN,
        Result
    };

private:
    std::string text;
    Type type;
    std::vector<std::string> next_keys;
    std::function<int(std::shared_ptr<Symmetry>)> correct_answer_func;
    PointGroupLabel result_point_group;

    int correct_answer;
    PointGroupLabel correct_point_group;
    int n;

public:
    /**
     * @brief Construct a new Practice Flowchart Step object
     *
     * This constructor should only be used with `type` equal to either
     * `Type::NoYes` or `Type::ChooseN`.
     *
     * @param text user-readable text
     * @param type step type
     * @param next_keys keys of next steps to show depending on the input
     * @param correct_answer_func lambda which returns the correct answer given
     * a symmetry object (as int, 1 for Yes and 0 for No in case of
     * `Type::NoYes`)
     */
    PracticeFlowchartStep(
        std::string text,
        Type type,
        std::vector<std::string> next_keys,
        std::function<int(std::shared_ptr<Symmetry>)> correct_answer_func
    );

    /**
     * @brief Construct a new Practice Flowchart Step object
     *
     * This constructor should only be used with `type` equal to
     * `Type::Result`.
     *
     * @param text user-readable text
     * @param type step type
     * @param result_point_group resulting point group
     */
    PracticeFlowchartStep(
        std::string text,
        Type type,
        PointGroupLabel result_point_group
    );

    /**
     * @brief Calculate the correct answer, given a symmetry
     *
     * @param symmetry
     */
    void calculate_correct_answer(std::shared_ptr<Symmetry> symmetry);

    /**
     * @brief Set the n parameter
     *
     * @param n
     */
    void set_n(int n);

    /**
     * @brief Get the text of the step
     *
     * @return const std::string
     */
    const std::string get_text() const;

    /**
     * @brief Get the type of the step
     *
     * @return const Type
     */
    const Type get_type() const;

    /**
     * @brief Get the keys of the next steps
     *
     * @return const std::vector<std::string>
     */
    const std::vector<std::string> get_next_keys() const;

    /**
     * @brief Get the correct answer
     *
     * This method should only be used with `type` equal to either
     * `Type::NoYes` or `Type::ChooseN`.
     *
     * @return const int
     */
    const int get_correct_answer() const;

    /**
     * @brief Get the resulting point group
     *
     * This method should only be used with `type` equal to `Type::Result`.
     *
     * @return const PointGroupLabel
     */
    const PointGroupLabel get_result_point_group() const;

    /**
     * @brief Get the correct point group
     *
     * This method should only be used with `type` equal to `Type::Result`.
     *
     * @return const PointGroupLabel
     */
    const PointGroupLabel get_correct_point_group() const;
};

#endif  // PRACTICE_PRACTICE_FLOWCHART_STEP_H
