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

#include "practice_flowchart_step.h"

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
PracticeFlowchartStep::PracticeFlowchartStep(
    std::string text,
    Type type,
    std::vector<std::string> next_keys,
    std::function<int(std::shared_ptr<Symmetry>)> correct_answer_func
) {
    if (type == Type::Result) {
        throw std::runtime_error("Provided next steps for a step with result type!");
    }

    this->text = text;
    this->type = type;
    this->next_keys = next_keys;
    this->correct_answer_func = correct_answer_func;
}

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
PracticeFlowchartStep::PracticeFlowchartStep(
    std::string text,
    Type type,
    PointGroupLabel result_point_group
) {
    if (type != Type::Result) {
        throw std::runtime_error("Provided result for a step without result type!");
    }

    this->text = text;
    this->type = type;
    this->result_point_group = result_point_group;
}

/**
 * @brief Calculate the correct answer, given a symmetry
 *
 * @param symmetry
 */
void PracticeFlowchartStep::calculate_correct_answer(std::shared_ptr<Symmetry> symmetry) {
    if (this->type != Type::Result) {
        this->correct_answer = this->correct_answer_func(symmetry);
    } else {
        this->correct_point_group = symmetry->get_point_group().get_label();
    }
}

/**
 * @brief Set the n parameter
 *
 * @param n
 */
void PracticeFlowchartStep::set_n(int n) {
    this->n = n;
}

/**
 * @brief Get the text of the step
 *
 * @return const std::string
 */
const std::string PracticeFlowchartStep::get_text() const {
    std::string text = this->text;
    // replace '{n}' by `this->n`
    size_t pos;
    while ((pos = text.find("{n}")) != std::string::npos) {
        text.replace(pos, 3, std::to_string(this->n));
    }
    // replace '{2n}' by `2 * this->n`
    while ((pos = text.find("{2n}")) != std::string::npos) {
        text.replace(pos, 4, std::to_string(2 * this->n));
    }
    return text;
}

/**
 * @brief Get the type of the step
 *
 * @return const Type
 */
const PracticeFlowchartStep::Type PracticeFlowchartStep::get_type() const {
    return this->type;
}

/**
 * @brief Get the keys of the next steps
 *
 * @return const std::vector<std::string>
 */
const std::vector<std::string> PracticeFlowchartStep::get_next_keys() const {
    return this->next_keys;
}

/**
 * @brief Get the correct answer
 *
 * This method should only be used with `type` equal to either
 * `Type::NoYes` or `Type::ChooseN`.
 *
 * @return const int
 */
const int PracticeFlowchartStep::get_correct_answer() const {
    if (this->type == Type::Result) {
        throw std::runtime_error("A step with result type does not have an answer!");
    }
    return this->correct_answer;
}

/**
 * @brief Get the resulting point group
 *
 * This method should only be used with `type` equal to `Type::Result`.
 *
 * @return const PointGroupLabel
 */
const PointGroupLabel PracticeFlowchartStep::get_result_point_group() const {
    if (this->type != Type::Result) {
        throw std::runtime_error("A step without result type does not have a resulting point group!");
    }
    if (n >= 2) {
        return PointGroupLabel(this->result_point_group.get_class(), this->n);
    } else {
        return this->result_point_group;
    }
}

/**
 * @brief Get the correct point group
 *
 * This method should only be used with `type` equal to `Type::Result`.
 *
 * @return const PointGroupLabel
 */
const PointGroupLabel PracticeFlowchartStep::get_correct_point_group() const {
    if (this->type != Type::Result) {
        throw std::runtime_error("A step without result type does not have a correct point group!");
    }
    return this->correct_point_group;
}
