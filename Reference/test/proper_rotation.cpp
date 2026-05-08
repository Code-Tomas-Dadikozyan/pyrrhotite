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
#include <vector>
#include <boost/test/unit_test.hpp>
#include <glm/glm.hpp>
#include "../src/structure.h"
#include "../src/symmetry/symmetry.h"
#include "../src/symmetry/operations/operation.h"
#include "../src/symmetry/operations/operation_label.h"
#include "utils.h"

BOOST_AUTO_TEST_SUITE(proper_rotation);

BOOST_AUTO_TEST_CASE(water) {
    std::string file = resolve_path("test/files/water.xyz");
    auto struc = std::make_shared<Structure>(file);

    Operation rotation_x(OperationLabel::Element::ProperRotation, 2, glm::vec3(1, 0, 0));
    rotation_x.do_operation(struc);

    BOOST_TEST(rotation_x.get_error() > 1);  // no C2(x)

    Operation rotation_y(OperationLabel::Element::ProperRotation, 2, glm::vec3(0, 1, 0));
    rotation_y.do_operation(struc);

    BOOST_TEST(rotation_y.get_error() > 1);  // no C2(y)

    Operation rotation_z(OperationLabel::Element::ProperRotation, 2, glm::vec3(0, 0, 1));
    rotation_z.do_operation(struc);

    BOOST_TEST(rotation_z.get_error() < 1e-7);  // C2(z)

    for (unsigned int degree = 3; degree <= 8; ++degree) {
        Operation rotation_n(OperationLabel::Element::ProperRotation, degree, glm::vec3(0, 0, 1));
        rotation_n.do_operation(struc);

        BOOST_TEST(rotation_n.get_error() > .5);  // no higher-degree rotations exist
    }
}

BOOST_AUTO_TEST_CASE(adamantane) {
    std::string file = resolve_path("test/files/adamantane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    unsigned int num_C2s = 0, num_C3s = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_degree() == 2) num_C2s++;
        if (rotation.get_degree() == 3) num_C3s++;
    }

    BOOST_TEST(num_C2s == 3);
    BOOST_TEST(num_C3s == 4);
    BOOST_TEST(proper_rotations.size() == 7);
}

BOOST_AUTO_TEST_CASE(benzene) {
    std::string file = resolve_path("test/files/benzene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    unsigned int num_C2s = 0, num_C3s = 0, num_C6s = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_degree() == 2) num_C2s++;
        if (rotation.get_degree() == 3) num_C3s++;
        if (rotation.get_degree() == 6) num_C6s++;
    }

    BOOST_TEST(num_C2s == 7);
    BOOST_TEST(num_C3s == 1);
    BOOST_TEST(num_C6s == 1);
    BOOST_TEST(proper_rotations.size() == 9);
}

BOOST_AUTO_TEST_CASE(dodecahydrododecaborate) {
    std::string file = resolve_path("test/files/dodecahydrododecaborate.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    unsigned int num_C2s = 0, num_C3s = 0, num_C5s = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_degree() == 2) num_C2s++;
        if (rotation.get_degree() == 3) num_C3s++;
        if (rotation.get_degree() == 5) num_C5s++;
    }

    BOOST_TEST(num_C2s == 15);
    BOOST_TEST(num_C3s == 10);
    BOOST_TEST(num_C5s == 6);
    BOOST_TEST(proper_rotations.size() == 31);
}

BOOST_AUTO_TEST_CASE(e_hex_3_ene) {
    std::string file = resolve_path("test/files/E-hex-3-ene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    BOOST_TEST(proper_rotations.size() == 0);
}

BOOST_AUTO_TEST_CASE(fluorochlorobromomethane) {
    std::string file = resolve_path("test/files/fluorochlorobromomethane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    BOOST_TEST(proper_rotations.size() == 0);
}

BOOST_AUTO_TEST_CASE(hydrazine) {
    std::string file = resolve_path("test/files/hydrazine.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    BOOST_TEST(proper_rotations.size() == 1);
    BOOST_TEST(proper_rotations[0].get_degree() == 2);
}

BOOST_AUTO_TEST_CASE(hydrogen_chloride) {
    std::string file = resolve_path("test/files/hydrogen-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    BOOST_TEST(proper_rotations.size() == 1);
    BOOST_TEST(proper_rotations[0].get_degree() == 0);  // 0 == Operation::DEGREE_INF
}

BOOST_AUTO_TEST_CASE(sulfur_hexafluoride) {
    std::string file = resolve_path("test/files/sulfur-hexafluoride.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    unsigned int num_C2s = 0, num_C3s = 0, num_C4s = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_degree() == 2) num_C2s++;
        if (rotation.get_degree() == 3) num_C3s++;
        if (rotation.get_degree() == 4) num_C4s++;
    }

    BOOST_TEST(num_C2s == 9);
    BOOST_TEST(num_C3s == 4);
    BOOST_TEST(num_C4s == 3);
    BOOST_TEST(proper_rotations.size() == 16);
}

BOOST_AUTO_TEST_CASE(tropylium) {
    std::string file = resolve_path("test/files/tropylium.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);
    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();

    unsigned int num_C2s = 0, num_C7s = 0;
    Operation C7;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_degree() == 2) num_C2s++;
        if (rotation.get_degree() == 7) {
            num_C7s++;
            C7 = rotation;
        }
    }

    BOOST_TEST(num_C2s == 7);
    BOOST_TEST(num_C7s == 1);
    BOOST_TEST(proper_rotations.size() == 8);

    std::vector<unsigned int> expected_indices_f = {1, 2, 3, 4, 5, 6, 0, 8, 9, 10, 11, 12, 13, 7};
    std::vector<unsigned int> expected_indices_b = {6, 0, 1, 2, 3, 4, 5, 13, 7, 8, 9, 10, 11, 12};
    for (unsigned int i = 0; i < struc->get_num_atoms(); ++i) {
        BOOST_TEST(C7.get_result_index(i) == expected_indices_f[i]);
    }

    C7.get_label().set_multiple(3);
    for (unsigned int i = 0; i < struc->get_num_atoms(); ++i) {
        BOOST_TEST(C7.get_result_index(i) == expected_indices_f[expected_indices_f[expected_indices_f[i]]]);
    }

    C7.get_label().set_multiple(-1);
    for (unsigned int i = 0; i < struc->get_num_atoms(); ++i) {
        BOOST_TEST(C7.get_result_index(i) == expected_indices_b[i]);
    }
}

BOOST_AUTO_TEST_SUITE_END();
