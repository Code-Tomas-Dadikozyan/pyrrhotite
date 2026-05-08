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

#include <memory>
#include <string>
#include <vector>
#include <boost/test/unit_test.hpp>
#include "../src/structure.h"
#include "../src/practice/practice_flowchart.h"
#include "../src/practice/practice_flowchart_step.h"
#include "../src/practice/practice_structure.h"
#include "../src/symmetry/symmetry.h"
#include "../src/symmetry/point_groups/point_group_label.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(practice_flowchart);

BOOST_AUTO_TEST_CASE(Dinfh) {
    std::string file = resolve_path("test/files/carbon-dioxide.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {1, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(0)->get_text() == "Is this molecule linear?");
    BOOST_TEST(flowchart.get_step(1)->get_text() == "Does this molecule contain an inversion center?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Dinfh);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(Cinfv) {
    std::string file = resolve_path("test/files/hydrogen-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {1, 0};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Cinfv);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(Ih) {
    std::string file = resolve_path("test/files/buckminsterfullerene.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 1, 1, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(1)->get_text() == "Does this molecule have two or more <i>C<sub>n</sub></i>, with <i>n</i> > 2?");
    BOOST_TEST(flowchart.get_step(2)->get_text() == "Does this molecule contain an inversion center?");
    BOOST_TEST(flowchart.get_step(3)->get_text() == "Does this molecule contain a <i>C</i><sub>5</sub> axis?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Ih);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(Oh) {
    std::string file = resolve_path("test/files/cubane.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 1, 1, 0};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Oh);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(Td) {
    std::string file = resolve_path("test/files/methane.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 1, 0};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Td);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(D3h) {
    std::string file = resolve_path("test/files/prismane.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 1, 3, 1, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(2)->get_text() == "Does this molecule have at least one proper rotational axis?");
    BOOST_TEST(flowchart.get_step(3)->get_text() == "Select the highest-order proper rotational axis (<i>C</i><sub><i>n</i></sub>).");
    BOOST_TEST(flowchart.get_step(4)->get_text() == "Are there 3 <i>C</i><sub>2</sub> axes perpendicular to the highest-order axis?");
    BOOST_TEST(flowchart.get_step(5)->get_text() == "Does this molecule contain a horizontal reflection plane (<i>σ</i><sub>h</sub>)?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Dh, 3);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(D6h) {
    std::string file = resolve_path("test/files/benzene.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 1, 6, 1, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(4)->get_text() == "Are there 6 <i>C</i><sub>2</sub> axes perpendicular to the highest-order axis?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Dh, 6);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(D2d) {
    std::string file = resolve_path("test/files/cyclooctatetraene.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 1, 2, 1, 0, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(6)->get_text() == "Does this molecule contain 2 dihedral reflection planes (<i>σ</i><sub>d</sub>)?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Dd, 2);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(D3) {
    std::string file = resolve_path("test/files/bicyclooctane.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 1, 3, 1, 0, 0};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::D, 3);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(C3h) {
    std::string file = resolve_path("test/files/boric-acid.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 1, 3, 0, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(5)->get_text() == "Does this molecule contain a horizontal reflection plane (<i>σ</i><sub>h</sub>)?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Ch, 3);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(C4v) {
    std::string file = resolve_path("test/files/pentaborane-9.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 1, 4, 0, 0, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(6)->get_text() == "Does this molecule contain 4 vertical reflection planes (<i>σ</i><sub>v</sub>)?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Cv, 4);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(C3) {
    std::string file = resolve_path("test/files/triethylamine.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 1, 3, 0, 0, 0, 0};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(7)->get_text() == "Does this molecule contain an improper rotational axis (<i>S</i><sub>6</sub>)?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::C, 3);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(Cs) {
    std::string file = resolve_path("test/files/thionyl-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 0, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(3)->get_text() == "Does this molecule contain a horizontal reflection plane (<i>σ</i><sub>h</sub>)?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Cs);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(Ci) {
    std::string file = resolve_path("test/files/E-hex-3-ene.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 0, 0, 1};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(4)->get_text() == "Does this molecule contain an inversion center?");
    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::Ci);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_CASE(C1) {
    std::string file = resolve_path("test/files/fluorochlorobromomethane.xyz");
    auto struc = std::make_shared<Structure>(file);
    auto symmetry = std::make_shared<Symmetry>(struc);
    auto practice_structure = std::make_shared<PracticeStructure>(symmetry);
    PracticeFlowchart flowchart(practice_structure);

    std::vector<int> answers = {0, 0, 0, 0, 0};

    for (unsigned int i = 0; i < answers.size(); ++i) {
        BOOST_TEST(flowchart.get_step(i)->get_correct_answer() == answers[i]);
        flowchart.handle_answer(i, answers[i]);
    }

    BOOST_TEST(flowchart.get_step(answers.size())->get_type() == PracticeFlowchartStep::Type::Result);
    PointGroupLabel correct = PointGroupLabel(PointGroupLabel::Class::C, 1);
    BOOST_TEST(flowchart.get_step(answers.size())->get_result_point_group().matches(correct));
    BOOST_TEST(flowchart.get_step(answers.size())->get_correct_point_group().matches(correct));
}

BOOST_AUTO_TEST_SUITE_END();
