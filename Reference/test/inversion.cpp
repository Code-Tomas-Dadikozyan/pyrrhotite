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

#include <memory>
#include <boost/test/unit_test.hpp>
#include "../src/structure.h"
#include "../src/symmetry/symmetry.h"
#include "../src/symmetry/operations/operation.h"
#include "../src/symmetry/operations/operation_label.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(inversion);

BOOST_AUTO_TEST_CASE(ammonia) {
    std::string file = resolve_path("test/files/ammonia.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() > 1);  // no inversion centre
}

BOOST_AUTO_TEST_CASE(benzene) {
    std::string file = resolve_path("test/files/benzene.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() < 1e-6);  // inversion centre
}

BOOST_AUTO_TEST_CASE(buckminsterfullerene) {
    std::string file = resolve_path("test/files/buckminsterfullerene.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() < 1e-6);  // inversion centre
}

BOOST_AUTO_TEST_CASE(carbon_dioxide) {
    std::string file = resolve_path("test/files/carbon-dioxide.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() < 1e-6);  // inversion centre
}

BOOST_AUTO_TEST_CASE(ferrocene_eclipsed) {
    std::string file = resolve_path("test/files/ferrocene-eclipsed.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() > .4);  // no inversion centre
}

BOOST_AUTO_TEST_CASE(ferrocene_staggered) {
    std::string file = resolve_path("test/files/ferrocene-staggered.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() < 1e-6);  // inversion centre
}

BOOST_AUTO_TEST_CASE(pentaborane_9) {
    std::string file = resolve_path("test/files/pentaborane-9.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() > 1.4);  // no inversion centre
}

BOOST_AUTO_TEST_CASE(thionyl_chloride) {
    std::string file = resolve_path("test/files/thionyl-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation inversion(OperationLabel::Element::Inversion);
    inversion.do_operation(struc);

    BOOST_TEST(inversion.get_error() == 2);  // no inversion centre
}

BOOST_AUTO_TEST_SUITE_END();
