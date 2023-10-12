import tempfile
import os
from flask import Flask, request, redirect, send_file, render_template, jsonify
from skimage import io, img_as_ubyte
from skimage.transform import resize
import base64
import glob
import numpy as np
from PIL import Image

app = Flask(__name__)

# model = load_model('model.h5')

main_html = """
<html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

   function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
   }

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");


      numero = getRndInteger(0, 10);
      numeros = [0,1,2,3,4,5,6,7,8,9];
      random = Math.floor(Math.random() * numeros.length);
      aleatorio = numeros[random];

      document.getElementById('mensaje').innerHTML  = 'Dibujando un ' + aleatorio;
      document.getElementById('numero').value = aleatorio;

      $('#myCanvas').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas').mouseup(function (e) {
          mousePressed = false;
      });
  	    $('#myCanvas').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      // Use the identity matrix while clearing the canvas
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  //https://www.askingbox.com/tutorial/send-html5-canvas-as-image-to-server
  function prepareImg() {
     var canvas = document.getElementById('myCanvas');
     document.getElementById('myImage').value = canvas.toDataURL();
  }



</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" ></script>
    <div align="center">
        <h1 id="title">PC2 - COMPUTACIÓN GRÁFICA</h1>
        <p style="text-align:center, font-size:20px">Ricardo Olivares Ventura - 20192002A</p>
        <p style="text-align:center, font-size:20px">Sergei Calle Cuadros</p>
        <p></p>
        <p></p>
        <p></p>
        <h1 id="subtitle">🚀LLenando el dataset de entrenamiento🚀</h1>
        <p></p>
        <p></p>
        <h1 id="mensaje">Dibujando...</h1>
        <canvas id="myCanvas" width="200" height="200" style="border:2px solid black"></canvas>
        <br/>
        <br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>
    <div align="center">
      <form method="post" action="upload" onsubmit="javascript:prepareImg();"  enctype="multipart/form-data">
      <input id="numero" name="numero" type="hidden" value="">
      <input id="myImage" name="myImage" type="hidden" value="">
      <input id="bt_upload" type="submit" value="Enviar">
      </form>
    </div>
</body>
</html>

"""

predictions_html = """
    <html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

   function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
   }

  function InitThis() {
      ctx = document.getElementById('myCanvas2').getContext("2d");


      numero = getRndInteger(0, 10);

      $('#myCanvas2').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas2').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas2').mouseup(function (e) {
          mousePressed = false;
      });
  	    $('#myCanvas2').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      // Use the identity matrix while clearing the canvas
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  //https://www.askingbox.com/tutorial/send-html5-canvas-as-image-to-server
  function prepareImg() {
     var canvas = document.getElementById('myCanvas2');
     document.getElementById('myImage2').value = canvas.toDataURL();
  }



</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" ></script>
    <div align="center">
        <h1 id="title">PC2 - COMPUTACIÓN GRÁFICA</h1>
        <p style="text-align:center, font-size:20px">Ricardo Olivares Ventura - 20192002A</p>
        <p style="text-align:center, font-size:20px">Sergei Calle Cuadros</p>
        <p></p>
        <p></p>
        <p></p>
        <h1 id="subtitle">🚀Prediciendo dígitos🚀</h1>
        <p></p>
        <p></p>
        <h1>Dibuja un número del 0 al 9</h1>
        <canvas id="myCanvas2" width="200" height="200" style="border:2px solid black"></canvas>
        <br/>
        <br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>
    <div align="center">
      <form method="post" action="upload_2" onsubmit="javascript:prepareImg();"  enctype="multipart/form-data">
      <input id="numero_2" name="numero_2" type="hidden" value="">
      <input id="myImage2" name="myImage2" type="hidden" value="">
      <input id="bt_upload_2" type="submit" value="Enviar">
      </form>
    </div>
</body>
</html>

"""

@app.route("/")
def main():
    return(main_html)

@app.route("/predictions")
def predictions():
    return(predictions_html)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        aleatorio = request.form.get('numero')
        print(aleatorio)
        with tempfile.NamedTemporaryFile(delete = False, mode = "w+b", suffix='.png', dir=str(aleatorio)) as fh:
            fh.write(base64.b64decode(img_data))
        print("Image uploaded")
    except Exception as err:
        print("Error occurred")
        print(err)

    return redirect("/", code=302)

""" @app.route('/upload_2', methods=['POST'])
def upload2():
    try:
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        image = np.array(Image.open(io.BytesIO(base64.b64decode(img_data))).convert('L'))
        image = resize(image, (28, 28))
        image = image / 255.0
        model = getModel()
        prediction = model.predict(np.expand_dims(image, axis=0))
        predicted_number = np.argmax(prediction)

        # Return prediction
        return jsonify({'predicted_number': int(predicted_number)})

    except Exception as err:
        print("Error occurred during image analysis")
        print(err)
        # return jsonify({'error': 'An error occurred during image analysis'})
    return redirect("/", code=302) """

@app.route('/prepare', methods=['GET'])
def prepare_dataset():
    images = []
    d = [0, 1, 2, 3 ,4 ,5 ,6 ,7 ,8 ,9]
    digits = []
    for digit in d:
      filelist = glob.glob('{}/*.png'.format(digit))
      images_read = io.concatenate_images(io.imread_collection(filelist))
      images_read = images_read[:, :, :, 3]
      digits_read = np.array([digit] * images_read.shape[0])
      images.append(images_read)
      digits.append(digits_read)
    images = np.vstack(images)
    digits = np.concatenate(digits)
    np.save('X.npy', images)
    np.save('y.npy', digits)
    return "OK!"

@app.route('/X.npy', methods=['GET'])
def download_X():
    return send_file('./X.npy')

@app.route('/y.npy', methods=['GET'])
def download_y():
    return send_file('./y.npy')

if __name__ == "__main__":
    digits = [0, 1, 2, 3 ,4 ,5 ,6 ,7 ,8 ,9]
    for d in digits:
        if not os.path.exists(str(d)):
            os.mkdir(str(d))
    app.run()
