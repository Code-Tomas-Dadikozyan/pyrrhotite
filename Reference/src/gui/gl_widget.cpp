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

#include "gl_widget.h"

/**
 * @brief Construct a new GLWidget object
 *
 * @param parent pointer to parent widget
 */
GLWidget::GLWidget(QWidget* parent): QOpenGLWidget(parent) {
    this->bg = parent->palette().color(QPalette::ColorRole::Window);
    this->model_manager = std::make_unique<ModelManager>();
    this->shader_program_manager = std::make_unique<ShaderProgramManager>();
    this->freetype_font = std::make_shared<FreeTypeFont>();
    this->structure_renderer = std::make_shared<StructureRenderer>(this->freetype_font);

    this->reset_camera();

    this->model_manager->add_model("sphere", Geometry::sphere());
    this->model_manager->add_model("cylinder", Geometry::cylinder());
    this->model_manager->add_model("cylinder_capped", Geometry::cylinder(true));
    this->model_manager->add_model("circle", Geometry::circle());
    this->model_manager->add_model("quad_3d", Geometry::quad_3d());

    this->model_manager->add_model("arrow", ObjLoader::load_from_obj(":/assets/models/arrow.obj"));
    this->model_manager->add_model("quad", Geometry::quad());

    connect(this, SIGNAL(frameSwapped()), this->structure_renderer.get(), SLOT(process_animations()));
    connect(this->structure_renderer.get(), SIGNAL(update()), this, SLOT(update()));
    connect(this->structure_renderer.get(), SIGNAL(animation_finished()), this, SIGNAL(animation_finished()));
}

/**
 * @brief Set the structure displayed in the widget
 *
 * @param structure
 * @param cartesian_axes matrix of unit vectors along which the Cartesian
 * axes should lie
 */
void GLWidget::set_structure(std::shared_ptr<Structure> structure, glm::mat3x3 cartesian_axes) {
    this->structure_renderer->set_structure(structure, cartesian_axes);
    this->reset_camera();
    this->update();
}

/**
 * @brief Get the structure renderer object
 *
 * @return const std::shared_ptr<StructureRenderer>
 */
const std::shared_ptr<StructureRenderer> GLWidget::get_structure_renderer() const {
    return this->structure_renderer;
}

/**
 * @brief Reset camera
 */
void GLWidget::reset_camera() {
    float camera_distance = 4 * this->structure_renderer->get_structure_span();
    this->camera_position = QVector3D(0.0, -camera_distance, 0.0);
    this->arcball_rotating = false;
    this->structure_renderer->reset_camera();
    this->update();
}

/**
 * @brief Set top left coordinates of widget on the screen and update
 */
void GLWidget::window_move_event() {
    this->top_left = this->mapToGlobal(QPoint(0, 0));
    this->update();
}

/**
 * @brief Initialise OpenGL environment
 */
void GLWidget::initializeGL() {
    connect(context(), &QOpenGLContext::aboutToBeDestroyed, this, &GLWidget::cleanup);
    initializeOpenGLFunctions();

    glClearColor(this->bg.redF(), this->bg.greenF(), this->bg.blueF(), 1.0f);

    this->model_manager->load_models_to_vao();
    this->freetype_font->initialize();

    this->load_shaders();

    this->initialize_frame_buffers();

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

/**
 * @brief Render scene
 */
void GLWidget::paintGL() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glEnable(GL_BLEND);
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE);
    glBlendEquation(GL_FUNC_ADD);

    if (this->stereoscopic_method == StereoscopicMethod::None) {
        this->paintGL_2d();
    } else {
        this->paintGL_stereoscopy();
    }

    // draw axes
    this->paint_gizmos();
}

/**
 * @brief Resize widget
 *
 * @param width widget width
 * @param height widget height
 */
void GLWidget::resizeGL(int width, int height) {
    this->projection.setToIdentity();
    this->projection.perspective(45.0f, GLfloat(width) / height, 0.01f, 1000.0f);

    this->resize_frame_buffers(width, height);
}

/**
 * @brief Handle mouse press event
 *
 * @param event
 */
void GLWidget::mousePressEvent(QMouseEvent* event) {
    if (event->buttons() & Qt::MouseButton::LeftButton) {
        this->arcball_rotating = true;
        this->mouse_position = event->pos();
    }
}

/**
 * @brief Handle mouse release event
 *
 * @param event
 */
void GLWidget::mouseReleaseEvent(QMouseEvent* event) {
    if (this->arcball_rotating && !(event->buttons() & Qt::MouseButton::LeftButton)) {
        this->structure_renderer->apply_arcball_rotation();
        this->arcball_rotating = false;
    }
}

/**
 * @brief Handle mouse move event
 *
 * @param event
 */
void GLWidget::mouseMoveEvent(QMouseEvent* event) {
    if (this->arcball_rotating) {
        // implementation from
        // https://en.wikibooks.org/wiki/OpenGL_Programming/Modern_OpenGL_Tutorial_Arcball
        if (event->x() != this->mouse_position.x() || event->y() != this->mouse_position.y()) {
            // calculate arcball vectors
            QVector3D va = this->calc_arcball_vector(this->mouse_position);
            QVector3D vb = this->calc_arcball_vector(event->pos());

            // calculate angle between vectors
            float dotprod = QVector3D::dotProduct(va, vb);
            if (qFabs(dotprod) > .9999f) return;
            float angle = qAcos(qMin(1.0f, dotprod));

            // rotation vector in camera space
            QVector3D axis_cam_space = QVector3D::crossProduct(va, vb).normalized();

            // matrix to change basis from camera to model space
            QMatrix3x3 cam_to_model_trans = this->view.inverted().toGenericMatrix<3, 3>();

            // rotation vector in model space
            QVector3D axis_model_space = QMatrix4x4(cam_to_model_trans) * axis_cam_space;
            glm::vec3 axis_model_space_ = glm::vec3(
                axis_model_space.x(),
                axis_model_space.y(),
                axis_model_space.z()
            );

            // set rotation
            this->structure_renderer->set_arcball_rotation(angle, axis_model_space_);

            this->update();
        }
    }
}

/**
 * @brief Handle mouse wheel event
 *
 * @param event
 */
void GLWidget::wheelEvent(QWheelEvent* event) {
    this->camera_position += event->angleDelta().y() * 0.01f * QVector3D(0, 1, 0);

    // prevent zooming in too far
    float min_camera_distance = 1.5 * this->structure_renderer->get_structure_span();
    if (this->camera_position[1] > -min_camera_distance) this->camera_position[1] = -min_camera_distance;

    this->update();
}

/**
 * @brief Initialize two frame buffers for stereoscopy
 */
void GLWidget::initialize_frame_buffers() {
    initializeOpenGLFunctions();

    glGenFramebuffers(FrameBuffer::Count, this->framebuffers);
    glGenTextures(FrameBuffer::Count, this->texture_color_buffers);
    glGenRenderbuffers(FrameBuffer::Count, this->rbo);

    QWindow *window_handle = this->window()->windowHandle();
    qreal pixel_ratio = window_handle->devicePixelRatio();
    float width = this->geometry().width() * pixel_ratio;
    float height = this->geometry().height() * pixel_ratio;

    for (unsigned int i = 0; i < FrameBuffer::Count; ++i) {
        glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[i]);
        glBindTexture(GL_TEXTURE_2D, this->texture_color_buffers[i]);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, this->texture_color_buffers[i], 0);

        glBindRenderbuffer(GL_RENDERBUFFER, this->rbo[i]);
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height);
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, this->rbo[i]);
    }
}

/**
 * @brief Resize the frame buffers
 *
 * @param width widget width
 * @param height widget height
 */
void GLWidget::resize_frame_buffers(int width, int height) {
    initializeOpenGLFunctions();

    QWindow *window_handle = this->window()->windowHandle();
    qreal pixel_ratio = window_handle->devicePixelRatio();
    float w = width * pixel_ratio;
    float h = height * pixel_ratio;

    for (unsigned int i = 0; i < FrameBuffer::Count; ++i) {
        glBindTexture(GL_TEXTURE_2D, this->texture_color_buffers[i]);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);

        glBindRenderbuffer(GL_RENDERBUFFER, this->rbo[i]);
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, w, h);
    }
}

/**
 * @brief Render scene in 2D
 */
void GLWidget::paintGL_2d() {
    Model *quad_model = this->model_manager->get_model("quad");

    // set camera
    QVector3D look_at = QVector3D(0.0f, 0.0f, 0.0f);
    this->view.setToIdentity();
    this->view.lookAt(this->camera_position, look_at, QVector3D(0.0f, 0.0f, 1.0f));

    // draw to silhouette frame buffer
    glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[FrameBuffer::Silhouette2D]);
    glEnable(GL_DEPTH_TEST);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // draw silhouette models
    this->paint_silhouette_models();

    // draw to label frame buffer
    glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[FrameBuffer::Labels2D]);
    glEnable(GL_DEPTH_TEST);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // draw silhouette models (ignore color)
    this->paint_silhouette_models(true);

    // draw labels
    this->paint_labels();

    // draw to structure frame buffer
    glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[FrameBuffer::Structure2D]);
    glEnable(GL_DEPTH_TEST);
    glClearColor(this->bg.redF(), this->bg.greenF(), this->bg.blueF(), 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // draw structure models
    this->paint_structure_models();

    // draw operation models
    this->paint_operation_models();

    // draw to screen
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glDisable(GL_DEPTH_TEST);
    glClear(GL_COLOR_BUFFER_BIT);

    ShaderProgram *canvas_shader = this->shader_program_manager->get_shader_program("canvas_shader");
    canvas_shader->bind();

    canvas_shader->set_uniform("silhouette_texture", 0);
    canvas_shader->set_uniform("labels_texture", 1);
    canvas_shader->set_uniform("structure_texture", 2);

    quad_model->draw(this->texture_color_buffers[FrameBuffer::Silhouette2D],
                     this->texture_color_buffers[FrameBuffer::Labels2D],
                     this->texture_color_buffers[FrameBuffer::Structure2D]);

    canvas_shader->release();

    glEnable(GL_DEPTH_TEST);
}

/**
 * @brief Render scene in stereoscopy
 */
void GLWidget::paintGL_stereoscopy() {
    const FrameBuffer framebuffers_side[2][4] = {
        {FrameBuffer::SilhouetteLeft, FrameBuffer::LabelsLeft, FrameBuffer::StructureLeft, FrameBuffer::StereoscopicLeft},
        {FrameBuffer::SilhouetteRight, FrameBuffer::LabelsRight, FrameBuffer::StructureRight, FrameBuffer::StereoscopicRight}
    };

    Model *quad_model = this->model_manager->get_model("quad");

    for (int i = 0; i < 2; ++i) {
        // set camera
        QVector3D look_at = QVector3D(0.0f, 0.0f, 0.0f);
        float eye_sep = -this->camera_position[1] / 30.0f;
        QVector3D camera_pos = this->camera_position + QVector3D((2 * i - 1) * eye_sep / 2.0, 0.0, 0.0);
        this->view.setToIdentity();
        this->view.lookAt(camera_pos, look_at, QVector3D(0.0f, 0.0f, 1.0f));

        // draw to silhouette frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[framebuffers_side[i][0]]);
        glEnable(GL_DEPTH_TEST);
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // draw silhouette models
        this->paint_silhouette_models();

        // draw to label frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[framebuffers_side[i][1]]);
        glEnable(GL_DEPTH_TEST);
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // draw silhouette models (ignore color)
        this->paint_silhouette_models(true);

        // draw labels
        this->paint_labels();

        // draw to structure frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[framebuffers_side[i][2]]);
        glEnable(GL_DEPTH_TEST);
        glClearColor(this->bg.redF(), this->bg.greenF(), this->bg.blueF(), 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        // draw structure models
        this->paint_structure_models();

        // draw operation models
        this->paint_operation_models();

        // draw to eye frame buffer
        glBindFramebuffer(GL_FRAMEBUFFER, this->framebuffers[framebuffers_side[i][3]]);
        glDisable(GL_DEPTH_TEST);
        glClear(GL_COLOR_BUFFER_BIT);

        ShaderProgram *canvas_shader = this->shader_program_manager->get_shader_program("canvas_shader");
        canvas_shader->bind();

        canvas_shader->set_uniform("silhouette_texture", 0);
        canvas_shader->set_uniform("labels_texture", 1);
        canvas_shader->set_uniform("structure_texture", 2);

        quad_model->draw(this->texture_color_buffers[framebuffers_side[i][0]],
                         this->texture_color_buffers[framebuffers_side[i][1]],
                         this->texture_color_buffers[framebuffers_side[i][2]]);

        canvas_shader->release();

        glEnable(GL_DEPTH_TEST);
    }

    // draw to screen
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glDisable(GL_DEPTH_TEST);
    glClear(GL_COLOR_BUFFER_BIT);

    ShaderProgram *stereoscopic_shader = this->shader_program_manager->get_shader_program(this->stereoscopic_method_name);
    stereoscopic_shader->bind();

    stereoscopic_shader->set_uniform("left_eye_texture", 0);
    stereoscopic_shader->set_uniform("right_eye_texture", 1);
    stereoscopic_shader->set_uniform("screen_x", this->top_left.x());
    stereoscopic_shader->set_uniform("screen_y", this->top_left.y());

    quad_model->draw(this->texture_color_buffers[FrameBuffer::StereoscopicLeft],
                     this->texture_color_buffers[FrameBuffer::StereoscopicRight]);

    stereoscopic_shader->release();

    glEnable(GL_DEPTH_TEST);
}

/**
 * @brief Paint all instances of structure models to the screen
 */
void GLWidget::paint_structure_models() {
    ShaderProgram *model_shader = this->shader_program_manager->get_shader_program("model_shader");
    model_shader->bind();

    for (ModelInstance instance : this->structure_renderer->get_structure_model_instances()) {
        Model *model = this->model_manager->get_model(instance.model_name);

        this->model = this->convert_glm_matrix(instance.transform);
        this->mvp = this->projection * this->view * this->model;

        model_shader->set_uniform("mvp", this->mvp);
        model_shader->set_uniform("view", this->view);
        model_shader->set_uniform("model", this->model);
        model_shader->set_uniform("color", QVector4D(instance.colour.x, instance.colour.y, instance.colour.z, instance.colour.a));
        model_shader->set_uniform("lightpos", QVector3D(0.0f, -1000.0f, 1.0f));

        model->draw();
    }

    model_shader->release();
}

/**
 * @brief Paint all instances of operation models to the screen
 */
void GLWidget::paint_operation_models() {
    ShaderProgram *model_shader = this->shader_program_manager->get_shader_program("model_shader");
    model_shader->bind();

    for (ModelInstance instance : this->structure_renderer->get_operation_model_instances()) {
        Model *model = this->model_manager->get_model(instance.model_name);

        this->model = this->convert_glm_matrix(instance.transform);
        this->mvp = this->projection * this->view * this->model;

        model_shader->set_uniform("mvp", this->mvp);
        model_shader->set_uniform("view", this->view);
        model_shader->set_uniform("model", this->model);
        model_shader->set_uniform("color", QVector4D(instance.colour.x, instance.colour.y, instance.colour.z, instance.colour.a));
        model_shader->set_uniform("lightpos", QVector3D(0.0f, -1000.0f, 1.0f));

        model->draw();
    }

    model_shader->release();
}

/**
 * @brief Paint all instances of silhouette models to the screen
 *
 * @param ignore_color use black for all models if true
 */
void GLWidget::paint_silhouette_models(bool ignore_color) {
    ShaderProgram *silhouette_shader = this->shader_program_manager->get_shader_program("silhouette_shader");
    silhouette_shader->bind();

    for (ModelInstance instance : this->structure_renderer->get_silhouette_model_instances()) {
        Model *model = this->model_manager->get_model(instance.model_name);

        this->model = this->convert_glm_matrix(instance.transform);
        this->mvp = this->projection * this->view * this->model;

        silhouette_shader->set_uniform("mvp", this->mvp);
        if (ignore_color) {
            silhouette_shader->set_uniform("color", QVector4D(0.0f, 0.0f, 0.0f, 1.0f));
        } else {
            silhouette_shader->set_uniform("color", QVector4D(instance.colour.x, instance.colour.y, instance.colour.z, instance.colour.a));
        }

        model->draw();
    }

    silhouette_shader->release();
}

/**
 * @brief Paint atom labels to the screen
 */
void GLWidget::paint_labels() {
    ShaderProgram *text_shader = this->shader_program_manager->get_shader_program("text_shader");
    text_shader->bind();

    for (ModelInstance instance : this->structure_renderer->get_label_model_instances()) {
        Model *model = this->model_manager->get_model(instance.model_name);

        this->model = this->convert_glm_matrix(instance.transform);
        this->mvp = this->projection * this->view * this->model;

        text_shader->set_uniform("mvp", this->mvp);
        text_shader->set_uniform("color", QVector4D(instance.colour.x, instance.colour.y, instance.colour.z, instance.colour.a));

        QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();
        f->glActiveTexture(GL_TEXTURE0);
        f->glBindTexture(GL_TEXTURE_2D, instance.texture_id);

        model->draw();
    }

    text_shader->release();
}

/**
 * @brief Paint axis gizmos
 */
void GLWidget::paint_gizmos() {
    ShaderProgram *axes_shader = this->shader_program_manager->get_shader_program("axes_shader");
    axes_shader->bind();

    const QVector3D r(1.0f      , 0.2117647f, 0.3254902f);
    const QVector3D g(0.5411765f, 0.854902f , 0.0235294f);
    const QVector3D b(0.172549f , 0.5607843f, 1.0f      );

    // set viewport, projection, and view matrices
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();
    QWindow *window_handle = this->window()->windowHandle();
    qreal pixel_ratio = window_handle->devicePixelRatio();
    float width = this->geometry().width() * pixel_ratio;
    float height = this->geometry().height() * pixel_ratio;
    f->glViewport(0.75f * width, 0.0f, 0.25f * width, 0.25f * height);

    QMatrix4x4 projection_ortho;
    projection_ortho.setToIdentity();
    float ratio = height / width;
    static const float size = 15.0f;
    projection_ortho.ortho(-size, size, -size * ratio, size * ratio, 0.1f, 1000.0f);

    this->view.setToIdentity();
    this->view.lookAt(QVector3D(0.0f, -10.0f, 0.0f), QVector3D(0.0f, 0.0f, 0.0f), QVector3D(0.0f, 0.0f, 1.0f));
    axes_shader->set_uniform("view", this->view);

    // draw the three axes
    Model *arrow_model = this->model_manager->get_model("arrow");
    QMatrix4x4 axis_rotation;

    // z axis
    axis_rotation.setToIdentity();
    this->model = this->convert_glm_matrix(this->structure_renderer->base_camera_matrix()) * axis_rotation;
    this->mvp = projection_ortho * this->view * this->model;
    axes_shader->set_uniform("model", this->model);
    axes_shader->set_uniform("mvp", this->mvp);
    axes_shader->set_uniform("color", b);
    arrow_model->draw();

    // y axis
    axis_rotation.setToIdentity();
    axis_rotation.rotate(-90.0f, QVector3D(1.0f, 0.0f, 0.0f));
    this->model = this->convert_glm_matrix(this->structure_renderer->base_camera_matrix()) * axis_rotation;
    this->mvp = projection_ortho * this->view * this->model;
    axes_shader->set_uniform("model", this->model);
    axes_shader->set_uniform("mvp", this->mvp);
    axes_shader->set_uniform("color", g);
    arrow_model->draw();

    // x axis
    axis_rotation.setToIdentity();
    axis_rotation.rotate(90.0f, QVector3D(0.0f, 1.0f, 0.0f));
    this->model = this->convert_glm_matrix(this->structure_renderer->base_camera_matrix()) * axis_rotation;
    this->mvp = projection_ortho * this->view * this->model;
    axes_shader->set_uniform("model", this->model);
    axes_shader->set_uniform("mvp", this->mvp);
    axes_shader->set_uniform("color", r);
    arrow_model->draw();

    axes_shader->release();
}

/**
 * @brief Load OpenGL shaders
 */
void GLWidget::load_shaders() {
    this->shader_program_manager->create_shader_program("model_shader", ShaderProgramType::ModelShader, ":/assets/shaders/phong.vs", ":/assets/shaders/phong.fs");
    this->shader_program_manager->create_shader_program("axes_shader", ShaderProgramType::AxesShader, ":/assets/shaders/axes.vs", ":/assets/shaders/axes.fs");
    this->shader_program_manager->create_shader_program("silhouette_shader", ShaderProgramType::SilhouetteShader, ":/assets/shaders/silhouette.vs", ":/assets/shaders/silhouette.fs");

    this->shader_program_manager->create_shader_program("canvas_shader", ShaderProgramType::CanvasShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/canvas.fs");

    this->shader_program_manager->create_shader_program("text_shader", ShaderProgramType::TextShader, ":/assets/shaders/text.vs", ":/assets/shaders/text.fs");

    this->shader_program_manager->create_shader_program("stereo_anaglyph_red_cyan", ShaderProgramType::StereoscopicShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/stereo_anaglyph_red_cyan.fs");
    this->shader_program_manager->create_shader_program("stereo_interlaced_rows_lr", ShaderProgramType::StereoscopicShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/stereo_interlaced_rows_lr.fs");
    this->shader_program_manager->create_shader_program("stereo_interlaced_rows_rl", ShaderProgramType::StereoscopicShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/stereo_interlaced_rows_rl.fs");
    this->shader_program_manager->create_shader_program("stereo_interlaced_columns_lr", ShaderProgramType::StereoscopicShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/stereo_interlaced_columns_lr.fs");
    this->shader_program_manager->create_shader_program("stereo_interlaced_columns_rl", ShaderProgramType::StereoscopicShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/stereo_interlaced_columns_rl.fs");
    this->shader_program_manager->create_shader_program("stereo_interlaced_checkerboard_lr", ShaderProgramType::StereoscopicShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/stereo_interlaced_checkerboard_lr.fs");
    this->shader_program_manager->create_shader_program("stereo_interlaced_checkerboard_rl", ShaderProgramType::StereoscopicShader, ":/assets/shaders/stereo.vs", ":/assets/shaders/stereo_interlaced_checkerboard_rl.fs");
}

/**
 * @brief Calculate the arcball vector
 *
 * @param pos position of the mouse cursor
 * @return QVector3D arcball vector
 */
QVector3D GLWidget::calc_arcball_vector(QPoint pos) {
    QVector3D P = QVector3D(1.0f * (float) pos.x() / (float) this->geometry().width() * 2.0f - 1.0f,
                            -(1.0f * (float) pos.y() / (float) this->geometry().height() * 2.0f - 1.0f),
                            0.0f);

    float OP_squared = P[0] * P[0] + P[1] * P[1];

    if (OP_squared <= 1.0f) {
        P[2] = qSqrt(1.0f - OP_squared);
    } else {
        P = P.normalized();
    }
    return P;
}

/**
 * @brief Convert GLM matrix to QMatrix
 *
 * @param matrix
 * @return QMatrix4x4
 */
QMatrix4x4 GLWidget::convert_glm_matrix(glm::mat4x4 matrix) {
    return QMatrix4x4(glm::value_ptr(matrix)).transposed();
}

/**
 * @brief Cleanup OpenGL environment
 */
void GLWidget::cleanup() {

}

/**
 * @brief Set the stereoscopic method and update
 *
 * @param action action corresponding to stereoscopic method
 */
void GLWidget::set_stereoscopic_method(QAction* action) {
    this->stereoscopic_method = action->data().value<StereoscopicMethod>();

    switch (this->stereoscopic_method) {
        case StereoscopicMethod::None:
            this->stereoscopic_method_name = "";
            break;
        case StereoscopicMethod::AnaglyphRedCyan:
            this->stereoscopic_method_name = "stereo_anaglyph_red_cyan";
            break;
        case StereoscopicMethod::InterlacedRowsLR:
            this->stereoscopic_method_name = "stereo_interlaced_rows_lr";
            break;
        case StereoscopicMethod::InterlacedRowsRL:
            this->stereoscopic_method_name = "stereo_interlaced_rows_rl";
            break;
        case StereoscopicMethod::InterlacedColumnsLR:
            this->stereoscopic_method_name = "stereo_interlaced_columns_lr";
            break;
        case StereoscopicMethod::InterlacedColumnsRL:
            this->stereoscopic_method_name = "stereo_interlaced_columns_rl";
            break;
        case StereoscopicMethod::InterlacedCheckerboardLR:
            this->stereoscopic_method_name = "stereo_interlaced_checkerboard_lr";
            break;
        case StereoscopicMethod::InterlacedCheckerboardRL:
            this->stereoscopic_method_name = "stereo_interlaced_checkerboard_rl";
            break;
        default:
            throw std::runtime_error("Unexpected stereoscopic method encountered.");
    }

    this->update();
}

/**
 * @brief Start animating a symmetry operation
 *
 * @param operation operation to animate
 */
void GLWidget::start_animation(Operation operation) {
    this->structure_renderer->start_animation(operation);
    this->update();
}

/**
 * @brief Set the operation visible in the widget
 *
 * @param operation_selected
 * @param selected_operation
 */
void GLWidget::set_operation(bool operation_selected, Operation selected_operation) {
    if (!this->structure_renderer->get_animating()) {
        if (operation_selected) {
            this->structure_renderer->set_operation(selected_operation);
        } else {
            this->structure_renderer->unset_operation();
        }
        this->update();
    }
}

/**
 * @brief Highlight atoms in the GL widget
 *
 * @param atoms atom indices to highlight
 */
void GLWidget::highlight_atoms(const QList<unsigned int>& atoms) {
    this->structure_renderer->unhighlight_atoms();
    for (unsigned int atom : atoms) {
        this->structure_renderer->highlight_atom(atom);
    }
    this->update();
}

/**
 * @brief Label atoms in the GL widget
 *
 * @param labels map of atom indices and labels
 */
void GLWidget::label_atoms(const QMap<unsigned int, std::string>& labels) {
    this->structure_renderer->clear_custom_labels();
    for (auto it = labels.constBegin(); it != labels.constEnd(); ++it) {
        this->structure_renderer->set_custom_label(it.key(), it.value());
    }
    this->update();
}
