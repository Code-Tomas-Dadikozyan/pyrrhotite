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

BOOST_TEST_DONT_PRINT_LOG_VALUE(OperationLabel::Plane);
BOOST_TEST_DONT_PRINT_LOG_VALUE(OperationLabel::Prime);

BOOST_AUTO_TEST_SUITE(operation_label);

BOOST_AUTO_TEST_CASE(adamantane) {
    std::string file = resolve_path("test/files/adamantane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    for (Operation& rotation : proper_rotations) {
        BOOST_TEST(rotation.get_label().get_prime() == OperationLabel::Prime::None);
    }

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    for (Operation& reflection : reflections) {
        BOOST_TEST(reflection.get_label().get_plane() == OperationLabel::Plane::Dihedral);
    }
}

BOOST_AUTO_TEST_CASE(ammonia) {
    std::string file = resolve_path("test/files/ammonia.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    for (Operation& rotation : proper_rotations) {
        BOOST_TEST(rotation.get_label().get_prime() == OperationLabel::Prime::None);
    }

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    for (Operation& reflection : reflections) {
        BOOST_TEST(reflection.get_label().get_plane() == OperationLabel::Plane::Vertical);
    }
}

BOOST_AUTO_TEST_CASE(bicyclooctane) {
    std::string file = resolve_path("test/files/bicyclooctane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    unsigned int num_no_prime = 0, num_single_prime = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
    }
    BOOST_TEST(num_no_prime == 1);
    BOOST_TEST(num_single_prime == 3);
}

BOOST_AUTO_TEST_CASE(biphenyl) {
    std::string file = resolve_path("test/files/biphenyl.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    unsigned int num_no_prime = 0, num_single_prime = 0, num_double_prime = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Double) num_double_prime++;
    }
    BOOST_TEST(num_no_prime == 1);
    BOOST_TEST(num_single_prime == 1);
    BOOST_TEST(num_double_prime == 1);
}

BOOST_AUTO_TEST_CASE(cyclobutadiene) {
    std::string file = resolve_path("test/files/cyclobutadiene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    unsigned int num_no_prime = 0, num_single_prime = 0, num_double_prime = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Double) num_double_prime++;
    }
    BOOST_TEST(num_no_prime == 2);
    BOOST_TEST(num_single_prime == 2);
    BOOST_TEST(num_double_prime == 2);

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    unsigned int num_h = 0, num_v = 0, num_d = 0;
    for (Operation& reflection : reflections) {
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Horizontal) num_h++;
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Vertical) num_v++;
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Dihedral) num_d++;
    }
    BOOST_TEST(num_h == 1);
    BOOST_TEST(num_v == 2);
    BOOST_TEST(num_d == 2);
}

BOOST_AUTO_TEST_CASE(diborane) {
    std::string file = resolve_path("test/files/diborane.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    unsigned int num_no_prime = 0, num_single_prime = 0, num_double_prime = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Double) num_double_prime++;
    }
    BOOST_TEST(num_no_prime == 1);
    BOOST_TEST(num_single_prime == 1);
    BOOST_TEST(num_double_prime == 1);

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    num_no_prime = 0; num_single_prime = 0;
    unsigned int num_h = 0, num_v = 0;
    for (Operation& reflection : reflections) {
        if (reflection.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (reflection.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Horizontal) num_h++;
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Vertical) num_v++;
    }
    BOOST_TEST(num_no_prime == 2);
    BOOST_TEST(num_single_prime == 1);
    BOOST_TEST(num_h == 1);
    BOOST_TEST(num_v == 2);
}

BOOST_AUTO_TEST_CASE(dodecahydrododecaborate) {
    std::string file = resolve_path("test/files/dodecahydrododecaborate.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    for (Operation& rotation : proper_rotations) {
        BOOST_TEST(rotation.get_label().get_prime() == OperationLabel::Prime::None);
    }

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    for (Operation& reflection : reflections) {
        BOOST_TEST(reflection.get_label().get_plane() == OperationLabel::Plane::None);
    }
}

BOOST_AUTO_TEST_CASE(ferrocene_staggered) {
    std::string file = resolve_path("test/files/ferrocene-staggered.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    unsigned int num_no_prime = 0, num_single_prime = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
    }
    BOOST_TEST(num_no_prime == 1);
    BOOST_TEST(num_single_prime == 5);

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    num_no_prime = 0; num_single_prime = 0;
    unsigned int num_h = 0, num_v = 0;
    for (Operation& reflection : reflections) {
        BOOST_TEST(reflection.get_label().get_plane() == OperationLabel::Plane::Dihedral);
    }
}

BOOST_AUTO_TEST_CASE(pentaborane_9) {
    std::string file = resolve_path("test/files/pentaborane-9.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    for (Operation& rotation : proper_rotations) {
        BOOST_TEST(rotation.get_label().get_prime() == OperationLabel::Prime::None);
    }

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    unsigned int num_v = 0, num_d = 0;
    for (Operation& reflection : reflections) {
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Vertical) num_v++;
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Dihedral) num_d++;
    }
    BOOST_TEST(num_v == 2);
    BOOST_TEST(num_d == 2);
}

BOOST_AUTO_TEST_CASE(sulfur_hexafluoride) {
    std::string file = resolve_path("test/files/sulfur-hexafluoride.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    unsigned int num_no_prime = 0, num_single_prime = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
    }
    BOOST_TEST(num_no_prime == 10);
    BOOST_TEST(num_single_prime == 6);

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    unsigned int num_h = 0, num_d = 0;
    for (Operation& reflection : reflections) {
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Horizontal) num_h++;
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Dihedral) num_d++;
    }
    BOOST_TEST(num_h == 3);
    BOOST_TEST(num_d == 6);
}

BOOST_AUTO_TEST_CASE(thionyl_chloride) {
    std::string file = resolve_path("test/files/thionyl-chloride.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    for (Operation& reflection : reflections) {
        BOOST_TEST(reflection.get_label().get_plane() == OperationLabel::Plane::Horizontal);
    }
}

BOOST_AUTO_TEST_CASE(trans_azobenzene) {
    std::string file = resolve_path("test/files/trans-azobenzene.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    for (Operation& rotation : proper_rotations) {
        BOOST_TEST(rotation.get_label().get_prime() == OperationLabel::Prime::None);
    }

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    for (Operation& reflection : reflections) {
        BOOST_TEST(reflection.get_label().get_plane() == OperationLabel::Plane::Horizontal);
    }
}

BOOST_AUTO_TEST_CASE(triethylamine) {
    std::string file = resolve_path("test/files/triethylamine.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    for (Operation& rotation : proper_rotations) {
        BOOST_TEST(rotation.get_label().get_prime() == OperationLabel::Prime::None);
    }
}

BOOST_AUTO_TEST_CASE(tropylium) {
    std::string file = resolve_path("test/files/tropylium.xyz");
    auto struc = std::make_shared<Structure>(file);
    Symmetry symmetry(struc);

    auto proper_rotations = symmetry.get_operation_manager()->get_proper_rotations();
    unsigned int num_no_prime = 0, num_single_prime = 0;
    for (Operation& rotation : proper_rotations) {
        if (rotation.get_label().get_prime() == OperationLabel::Prime::None) num_no_prime++;
        if (rotation.get_label().get_prime() == OperationLabel::Prime::Single) num_single_prime++;
    }
    BOOST_TEST(num_no_prime == 1);
    BOOST_TEST(num_single_prime == 7);

    auto reflections = symmetry.get_operation_manager()->get_reflections();
    unsigned int num_h = 0, num_v = 0;
    for (Operation& reflection : reflections) {
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Horizontal) num_h++;
        if (reflection.get_label().get_plane() == OperationLabel::Plane::Vertical) num_v++;
    }
    BOOST_TEST(num_h == 1);
    BOOST_TEST(num_v == 7);
}

BOOST_AUTO_TEST_SUITE_END();
