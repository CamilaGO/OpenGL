import pygame
import numpy
import glm
import pyassimp

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
clock = pygame.time.Clock()

vertex_shader = """
#version 460
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texcoords;

uniform mat4 theMatrix;
uniform vec3 light;
uniform float time;

out float intensity;
out vec2 vertexTexcoords;
out vec3 v3Position;
out vec3 fnormal;
out float ftime;

void main()
{
	fnormal = normal;
	vertexTexcoords = texcoords;
	v3Position = position;
	ftime = time;
	intensity = dot(normal, normalize(light));
	gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{

	fragColor = texture(tex, vertexTexcoords);
}
"""

psycho_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec3 fnormal;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	fragColor = vec4(fnormal, 1.1);
}
"""

cola_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec3 v3Position;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	float bright = floor(mod(v3Position.x*10.0, 2.0)+.2) + floor(mod(v3Position.y*1.0, 1.0)+.5) + floor(mod(v3Position.z*0.0, 10.0)+.5);
  	fragColor = mod(bright, 6.0) > .8 ? vec4(1.0, 0.0, 0.0, 9.0) : vec4(1.0, 3.0, 2.0, 0.5);
}
"""

timer_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec3 v3Position;
in float ftime;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	float tiempo = ftime*15.5;
	float bright = floor(mod(v3Position.z*tiempo, 0.5)+ftime) + floor(mod(v3Position.y*tiempo, 0.5)+ftime) + floor(mod(v3Position.x*ftime, 25.0));
    vec4 color = mod(bright, 2.0) > .8 ? vec4(0.0, 1.5, 1.5, 9.0) : vec4(10.0, 0.0, 0.0, 0.0);
  	fragColor = color * intensity;
}
"""

party_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

in float intensity;
in vec2 vertexTexcoords;
in vec3 v3Position;
in float ftime;
in vec3 fnormal;

uniform sampler2D tex;
uniform vec4 diffuse;
uniform vec4 ambient;

void main()
{
	float theta = ftime*20.0;
  
	vec3 dir1 = vec3(cos(theta),0,sin(theta)); 
	vec3 dir2 = vec3(sin(theta),0,cos(theta));
  
	float diffuse1 = pow(dot(fnormal,dir1),2.0);
	float diffuse2 = pow(dot(fnormal,dir2),2.0);
		
	vec3 col1 = diffuse1 * vec3(1,0,0);
	vec3 col2 = diffuse2 * vec3(0,0,1);
    gl_FragColor = vec4(col1 + col2, 1.0);
}
"""

shader = compileProgram(
		compileShader(vertex_shader, GL_VERTEX_SHADER),
		compileShader(fragment_shader, GL_FRAGMENT_SHADER)
)


scene = pyassimp.load('./tiger.obj')

pygame.mixer.music.load('./TigerEye.mp3')
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(0)

def getTexture(name):
	textName = './' + name + '.jpg'
	texture_surface = pygame.image.load(textName)
	texture_data = pygame.image.tostring(texture_surface, 'RGB')
	width = texture_surface.get_width()
	height = texture_surface.get_height()

	view = glm.mat4(1)
	projection = glm.perspective(glm.radians(45),800/600,0.1,1000.0)
	model = glm.mat4(1)

	texture = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, texture)
	glTexImage2D(
		GL_TEXTURE_2D,
		0,
		GL_RGB,
		width,
		height,
		0,
		GL_RGB,
		GL_UNSIGNED_BYTE,
		texture_data
	)
	glGenerateMipmap(GL_TEXTURE_2D)

getTexture("tiger")

def glize(node):
	# render
	for mesh in node.meshes:
		vertex_data = numpy.hstack([
			numpy.array(mesh.vertices, dtype=numpy.float32),
			numpy.array(mesh.normals, dtype=numpy.float32),
			numpy.array(mesh.texturecoords[0], dtype=numpy.float32),
		])

		index_data = numpy.hstack(
			numpy.array(mesh.faces, dtype=numpy.int32),
		)

		vertex_buffer_object = glGenVertexArrays(1)
		glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
		glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(0))
		glEnableVertexAttribArray(0)
		glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(3 * 4))
		glEnableVertexAttribArray(1)
		glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(6 * 4))
		glEnableVertexAttribArray(2)

		element_buffer_object = glGenBuffers(1)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)


		glUniform3f(
			glGetUniformLocation(shader, "light"),
			-100, 185, 0.2
		)

		glUniform4f(
			glGetUniformLocation(shader, "diffuse"),
			0.7, 0.2, 0, 1
		)

		glUniform4f(
			glGetUniformLocation(shader, "ambient"),
			0.2, 0.2, 0.2, 1
		)


		glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

	for child in node.children:
		glize(child)


camera = glm.vec3(0,0,200)
camera_speed = 20


i = glm.mat4()

def createTheMatrix(counter, camera):
	translate = glm.translate(i, glm.vec3(0,0,0))
	rotate = glm.rotate(i, glm.radians(counter), glm.vec3(0,1,0))
	scale = glm.scale(i, glm.vec3(0.25,0.25,0.25))

	model = translate * rotate * scale
	view = glm.lookAt(camera, glm.vec3(0,0,0), glm.vec3(0,1,0))
	projection = glm.perspective(glm.radians(45), 800/600, 0.1, 1000)

	return projection * view * model

glViewport(0, 0, 800, 600)

glEnable(GL_DEPTH_TEST)

paused = False
running = True
counter = 0
timeshader = 0
while running:
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glClearColor(0.58, 0.58, 0.58, 1.0)
	#glClearColor(0.7, 1.0, 0.7, 1.0) #el cuarto parametro es la transparencia

	glUseProgram(shader)

	theMatrix = createTheMatrix(counter, camera)

	theMatrixLocation = glGetUniformLocation(shader, 'theMatrix')

	glUniformMatrix4fv(
	theMatrixLocation, #location
	1, # count
	GL_FALSE, 
	glm.value_ptr(theMatrix)
	)

	timeshader += 0.01

	glUniform1f(
		glGetUniformLocation(shader, 'time'),
		timeshader
	)

	# glDrawArrays(GL_TRIANGLES, 0, 3)
	# glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
	glize(scene.rootnode)

	pygame.display.flip()
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
			if event.key == pygame.K_f:
				glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
			if event.key == pygame.K_LEFT:
				camera.x -= camera_speed
			if event.key == pygame.K_RIGHT:
				camera.x += camera_speed
			if event.key == pygame.K_UP:
				camera.y -= camera_speed
			if event.key == pygame.K_DOWN:
				camera.y += camera_speed
			if event.key == pygame.K_l:
				getTexture("leopardo")
			if event.key == pygame.K_t:
				getTexture("tiger")
			if event.key == pygame.K_p:
				getTexture("panther")
			if event.key == pygame.K_o:
				getTexture("wolf")
			if event.key == pygame.K_s:
				getTexture("wtiger")
			if event.key == pygame.K_a:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(fragment_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_b:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(psycho_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_c:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(cola_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
				pygame.mixer.music.load('./cocaSong.mp3')
				pygame.mixer.music.set_volume(0.8)
				pygame.mixer.music.play(0)
			if event.key == pygame.K_z:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(timer_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
			if event.key == pygame.K_x:
				shader = compileProgram(
						compileShader(vertex_shader, GL_VERTEX_SHADER),
						compileShader(party_shader, GL_FRAGMENT_SHADER)
				)
				glUseProgram(shader)
				pygame.mixer.music.load('./partyRock.mp3')
				pygame.mixer.music.set_volume(0.8)
				pygame.mixer.music.play(0)
			if event.key == pygame.K_SPACE:
				paused = not paused

	if not paused:
		counter += 1
	clock.tick(0) #esto hace que la vuelta sea mas lenta