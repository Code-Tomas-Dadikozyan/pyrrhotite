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

#ifndef GUI_GL_WIDGET_H
#define GUI_GL_WIDGET_H

#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <Qt>
#include <QtMath>
#include <QAction>
#include <QList>
#include <QMap>
#include <QMatrix4x4>
#include <QMouseEvent>
#include <QOpenGLContext>
#include <QOpenGLFunctions>
#include <QOpenGLWidget>
#include <QPalette>
#include <QPoint>
#include <QVector3D>
#include <QWheelEvent>
#include <QWidget>
#include <QWindow>
#include "../structure.h"
#include "../structure_renderer.h"
#include "../periodic_table/element.h"
#include "../periodic_table/periodic_table.h"
#include "../symmetry/operations/operation.h"
#include "../symmetry/operations/operation_label.h"
#include "models/geometry.h"
#include "models/model.h"
#include "models/model_manager.h"
#include "models/obj_loader.h"
#include "models/quad_model.h"
#include "shaders/shader_program_manager.h"
#include "shaders/shader_program_type.h"
#include "text/freetype_font.h"
#include "stereoscopic_method.h"

class GLWidget: public QOpenGLWidget, protected QOpenGLFunctions {
    Q_OBJECT

private:
    enum FrameBuffer {
        Structure2D,
        StructureLeft,
        StructureRight,
        Silhouette2D,
        SilhouetteLeft,
        SilhouetteRight,
        Labels2D,
        LabelsLeft,
        LabelsRight,
        StereoscopicLeft,
        StereoscopicRight,
        Count
    };

    QColor bg;

    std::unique_ptr<ModelManager> model_manager;
    std::unique_ptr<ShaderProgramManager> shader_program_manager;
    std::shared_ptr<FreeTypeFont> freetype_font;

    std::shared_ptr<StructureRenderer> structure_renderer;
    std::shared_ptr<Structure> structure;

    QPoint top_left;

    QMatrix4x4 projection;
    QMatrix4x4 view;
    QMatrix4x4 model;
    QMatrix4x4 mvp;
    QVector3D camera_position;

    bool arcball_rotating = false;  // whether arcball rotation is active
    QPoint mouse_position;  // at start of arcball rotation

    unsigned int framebuffers[FrameBuffer::Count];
    unsigned int texture_color_buffers[FrameBuffer::Count];
    unsigned int rbo[FrameBuffer::Count];

    StereoscopicMethod stereoscopic_method = StereoscopicMethod::None;
    std::string stereoscopic_method_name;

public:
    /**
     * @brief Construct a new GLWidget object
     *
     * @param parent pointer to parent widget
     */
    GLWidget(QWidget* parent);

    /**
     * @brief Set the structure displayed in the widget
     *
     * @param structure
     * @param cartesian_axes matrix of unit vectors along which the Cartesian
     * axes should lie
     */
    void set_structure(std::shared_ptr<Structure> structure, glm::mat3x3 cartesian_axes);

    /**
     * @brief Get the structure renderer object
     *
     * @return const std::shared_ptr<StructureRenderer>
     */
    const std::shared_ptr<StructureRenderer> get_structure_renderer() const;

    /**
     * @brief Reset camera
     */
    void reset_camera();

    /**
     * @brief Set top left coordinates of widget on the screen and update
     */
    void window_move_event();

protected:
    /**
     * @brief Initialise OpenGL environment
     */
    void initializeGL() Q_DECL_OVERRIDE;

    /**
     * @brief Render scene
     */
    void paintGL() Q_DECL_OVERRIDE;

    /**
     * @brief Resize widget
     *
     * @param width widget width
     * @param height widget height
     */
    void resizeGL(int width, int height) Q_DECL_OVERRIDE;

    /**
     * @brief Handle mouse press event
     *
     * @param event
     */
    void mousePressEvent(QMouseEvent* event) Q_DECL_OVERRIDE;

    /**
     * @brief Handle mouse release event
     *
     * @param event
     */
    void mouseReleaseEvent(QMouseEvent* event) Q_DECL_OVERRIDE;

    /**
     * @brief Handle mouse move event
     *
     * @param event
     */
    void mouseMoveEvent(QMouseEvent* event) Q_DECL_OVERRIDE;

    /**
     * @brief Handle mouse wheel event
     *
     * @param event
     */
    void wheelEvent(QWheelEvent* event) Q_DECL_OVERRIDE;

private:
    /**
     * @brief Initialize two frame buffers for stereoscopy
     */
    void initialize_frame_buffers();

    /**
     * @brief Resize the frame buffers
     *
     * @param width widget width
     * @param height widget height
     */
    void resize_frame_buffers(int width, int height);

    /**
     * @brief Render scene in 2D
     */
    void paintGL_2d();

    /**
     * @brief Render scene in stereoscopy
     */
    void paintGL_stereoscopy();

    /**
     * @brief Paint all instances of structure models to the screen
     */
    void paint_structure_models();

    /**
     * @brief Paint all instances of operation models to the screen
     */
    void paint_operation_models();

    /**
     * @brief Paint all instances of silhouette models to the screen
     *
     * @param ignore_color use black for all models if true
     */
    void paint_silhouette_models(bool ignore_color = false);

    /**
     * @brief Paint atom labels to the screen
     */
    void paint_labels();

    /**
     * @brief Paint axis gizmos
     */
    void paint_gizmos();

    /**
     * @brief Load OpenGL shaders
     */
    void load_shaders();

    /**
     * @brief Calculate the arcball vector
     *
     * @param pos position of the mouse cursor
     * @return QVector3D arcball vector
     */
    QVector3D calc_arcball_vector(QPoint pos);

    /**
     * @brief Convert GLM matrix to QMatrix
     *
     * @param matrix
     * @return QMatrix4x4
     */
    QMatrix4x4 convert_glm_matrix(glm::mat4x4 matrix);

public slots:
    /**
     * @brief Cleanup OpenGL environment
     */
    void cleanup();

    /**
     * @brief Set the stereoscopic method and update
     *
     * @param action action corresponding to stereoscopic method
     */
    void set_stereoscopic_method(QAction* action);

    /**
     * @brief Start animating an operation
     *
     * @param operation
     */
    void start_animation(Operation operation);

    /**
     * @brief Set the operation visible in the widget
     *
     * @param operation_selected
     * @param selected_operation
     */
    void set_operation(bool operation_selected, Operation selected_operation);

    /**
     * @brief Highlight atoms in the GL widget
     *
     * @param atoms atom indices to highlight
     */
    void highlight_atoms(const QList<unsigned int>& atoms);

    /**
     * @brief Label atoms in the GL widget
     *
     * @param labels map of atom indices and labels
     */
    void label_atoms(const QMap<unsigned int, std::string>& labels);

signals:
    /**
     * @brief Signal to send when the current animation has finished
     */
    void animation_finished();
};

#endif  // GUI_GL_WIDGET_H
