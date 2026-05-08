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
#include <glm/glm.hpp>
#include "../src/structure.h"
#include "../src/symmetry/symmetry.h"
#include "../src/symmetry/operations/operation.h"
#include "../src/symmetry/operations/operation_label.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(improper_rotation)

BOOST_AUTO_TEST_CASE(boric_acid) {
    std::string file = resolve_path("test/files/boric-acid.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation rotation_x(OperationLabel::Element::ImproperRotation, 3, glm::vec3(1, 0, 0));
    rotation_x.do_operation(struc);

    BOOST_TEST(rotation_x.get_error() > 1);  // no S3(x)

    Operation rotation_y(OperationLabel::Element::ImproperRotation, 3, glm::vec3(0, 1, 0));
    rotation_y.do_operation(struc);

    BOOST_TEST(rotation_y.get_error() > 1);  // no S3(y)

    Operation rotation_z(OperationLabel::Element::ImproperRotation, 3, glm::vec3(0, 0, 1));
    rotation_z.do_operation(struc);

    BOOST_TEST(rotation_z.get_error() < 1e-6);  // S3(z)

    for (unsigned int degree = 2; degree <= 8; ++degree) {
        if (degree == 3) continue;
        Operation rotation_n(OperationLabel::Element::ImproperRotation, degree, glm::vec3(0, 0, 1));
        rotation_n.do_operation(struc);

        BOOST_TEST(rotation_n.get_error() > .5);  // no other-degree rotations exist
    }
}

BOOST_AUTO_TEST_CASE(carbon_dioxide) {
    std::string file = resolve_path("test/files/carbon-dioxide.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    BOOST_TEST(improper_rotations.size() == 1);
    BOOST_TEST(improper_rotations[0].get_degree() == 0);  // 0 == Operation::DEGREE_INF
}

BOOST_AUTO_TEST_CASE(coronene) {
    std::string file = resolve_path("test/files/coronene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    unsigned int num_S3s = 0, num_S6s = 0;
    for (Operation& rotation : improper_rotations) {
        if (rotation.get_degree() == 3) num_S3s++;
        if (rotation.get_degree() == 6) num_S6s++;
    }

    BOOST_TEST(num_S3s == 1);
    BOOST_TEST(num_S6s == 1);
    BOOST_TEST(improper_rotations.size() == 2);
}

BOOST_AUTO_TEST_CASE(cubane) {
    std::string file = resolve_path("test/files/cubane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    unsigned int num_S4s = 0, num_S6s = 0;
    for (Operation& rotation : improper_rotations) {
        if (rotation.get_degree() == 4) num_S4s++;
        if (rotation.get_degree() == 6) num_S6s++;
    }

    BOOST_TEST(num_S4s == 3);
    BOOST_TEST(num_S6s == 4);
    BOOST_TEST(improper_rotations.size() == 7);
}

BOOST_AUTO_TEST_CASE(cyclooctatetraene) {
    std::string file = resolve_path("test/files/cyclooctatetraene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    BOOST_TEST(improper_rotations.size() == 1);
    BOOST_TEST(improper_rotations[0].get_degree() == 4);
}

BOOST_AUTO_TEST_CASE(dodecahydrododecaborate) {
    std::string file = resolve_path("test/files/dodecahydrododecaborate.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    unsigned int num_S6s = 0, num_S10s = 0;
    for (Operation& rotation : improper_rotations) {
        if (rotation.get_degree() == 6) num_S6s++;
        if (rotation.get_degree() == 10) num_S10s++;
    }

    BOOST_TEST(num_S6s == 10);
    BOOST_TEST(num_S10s == 6);
    BOOST_TEST(improper_rotations.size() == 16);
}

BOOST_AUTO_TEST_CASE(hydrogen_chloride) {
    std::string file = resolve_path("test/files/hydrogen-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    BOOST_TEST(improper_rotations.size() == 0);
}

BOOST_AUTO_TEST_CASE(methane) {
    std::string file = resolve_path("test/files/methane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    unsigned int num_S4s = 0;
    for (Operation& rotation : improper_rotations) {
        if (rotation.get_degree() == 4) num_S4s++;
    }

    BOOST_TEST(num_S4s == 3);
    BOOST_TEST(improper_rotations.size() == 3);
}

BOOST_AUTO_TEST_CASE(triethylamine) {
    std::string file = resolve_path("test/files/triethylamine.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    BOOST_TEST(improper_rotations.size() == 0);
}

BOOST_AUTO_TEST_CASE(water) {
    std::string file = resolve_path("test/files/water.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto improper_rotations = symmetry.get_operation_manager()->get_improper_rotations();

    BOOST_TEST(improper_rotations.size() == 0);
}

BOOST_AUTO_TEST_SUITE_END();
