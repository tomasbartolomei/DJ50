
from youtubesearchpython import VideosSearch
import json
import requests
import pytube
from pydub import AudioSegment
import re
from pathlib import Path

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'


def welcome_message():
    """Imprime un mensaje de inicio del progama y contiene informacion de como usarlo"""
    return "\nTHIS IS DJ50, BE A DJ SUPER STAR...\n An easy way to create your DJ set by extracting songs from YouTube\n"

def info():
    return"SEARCH YOUR TRACKS IN YOUTUBE: Type your name song, check title and duration. Confirm if you want to add it.\nHOW TO MIX BETWEEN SONGS? Choose crossfade time expressed in seconds.\nADDING DJ SOUNDS: Add a file path of your sound. Choose how many to add and where to place it.\nEXPORT AUDIO: Export audio in mp3 file to enjoy your music!!\n\n"


def crossfade_time():
    """Pregunta cuanto es el tiempo de crossfade entre dos tracks. El input tiene que se un int entre 0 y 60.
    Luego se multiplica por 1000 porque la libreria trabaja en milisegundos y nosotros queremos segundos."""

    while True:
        try:
            crossfade = int(input("Crossfade time between this tracks (express in seconds, min: 0 - max: 60): "))
            if crossfade < 0 or crossfade > 60:
                pass
            else:
                return (crossfade * 1000)
        except:
            print("Invalid number, try again")


def search_first_track():
    """Devuelve el link de una busqueda de youtube. Se una esta funcion solo para obtener el primer track del djset.
    En caso de que haya un error, vuelve a preguntar hasta conseguir el primer track.
    Imprime titulo y duracion del track para saber si el usuario esta de acuerdo o busca otro track."""
    
    while True:
        #BUSCAR TRACK EN YOUTUBE
        tracksearch = input("Search in YouTube: ")
        #SOLICITA INFORMACION DEL TRACK, LIMITADO A 1 SOLO PEDIDO.
        videosSearch = VideosSearch(tracksearch, limit = 1)
        response = videosSearch.result()
        #BUSCAR EL TITULO Y LA DURACION DEL TRACK
        title = response['result'][0]['title']
        duration = response['result'][0]['duration']
        #IMPRIMIR EL NOMBRE
        print("Title:", title, "Duration:", duration)
        #PREGUNTAR SI ESTA OK
        question = input("Do you want to add this track?: ")
        #DOS DIRECCIONES DE RESPUESTA
        if question == "yes":
            return response['result'][0]['link']
        else:
            pass



def download_track(url):
    """Argumento: link de youtube.
    Descarga el track en formato de audio .mp4.
    Devuelve un objeto audiosegment"""
    yt=pytube.YouTube(url)
    t=yt.streams.filter(only_audio=True)
    t[0].download(output_path=None)
    audio_file_name = yt.title + ".mp4"
    track = AudioSegment.from_file(audio_file_name)
    return track

def loop_tracks(first_track_file):
    """Argumento: objeto de audio del primer track del set.
    Descarga los tracks y los va agregando al primer track, los engancha segun la funcion crossfade time.
    Imprime pregunta de si deseamos seguir agregando tracks o si deseamos finalizar."""
    while True:
        try:
            #BUSCAR TRACK EN YOUTUBE
            tracksearch = input("Search in YouTube: ")
            #SOLICITA INFORMACION DEL TRACK, LIMITADO A 1 SOLO PEDIDO.
            videosSearch = VideosSearch(tracksearch, limit = 1)
            response = videosSearch.result()
            #BUSCAR EL TITULO Y LA DURACION DEL TRACK
            title = response['result'][0]['title']
            duration = response['result'][0]['duration']
            #IMPRIMIR EL NOMBRE
            print("Title:", title, "Duration:", duration)
            #PREGUNTAR SI ESTA OK
            pregunta = input("Do you want to add this track?: ")
            #DOS DIRECCIONES DE RESPUESTA
            if pregunta == "yes":
                track_file = download_track(response['result'][0]['link'])
                cross = crossfade_time()
                first_track_file = first_track_file.append(track_file, crossfade=cross)#CROSSFADE TRABAJA EN MILISEGUNDOS, VER COMO PASAR A SEGUNDOS. VER COMO PREGUNTO EN CADA TRACK CUANTO DURA EL ENGANCHE
                finish_adding_tracks = input("Do you want to add more tracks to your DJ set? ")
                if finish_adding_tracks == "yes":
                    pass
                else:
                    return first_track_file #REPREGUNTAR SI QUERE SEGUIR O QUIERE TERMINAR EL SET.
            else:
                pass
        except:
            print("This track cant be added")

def export(djset):
    """Pregunta nombre para el archivo del set. Solo deja poner letras en minuscula y numeros. Agrega el ".mp3" """
    try:
        name_djset = input("How would you like to name your DJ set file? ")
        #saca espacios y hace todo minuscula
        name_djset = name_djset.replace(" ", "").lower()
        #limpia el string x si tiene algo que no sean numeros o letras
        name_djset = re.sub(r'[^a-zA-Z0-9]', '', name_djset)
        djset.export(name_djset + ".mp3", format="mp3", bitrate="320k")
        print("The download has been completed. Look for the file in your folder.")
    except:
        print("Cant export DJ Set")

def duracion_set(set):
    """Deveulve la duracion del djset en minutos y segundos y luego la totalidad en segundos para que el usaurio sepa donde poner su dj signature"""
    duration_in_milisec = len(set)
    duration_in_sec = round(duration_in_milisec / 1000)
    minutes,seconds = divmod(duration_in_sec, 60)
    return minutes, seconds, duration_in_sec

def overlay_sounds(audio_final,q_overlay, segundos):
    """Argumentos: objeto de audio del set final. Cantidad de overlay que quiere agregar (5max) y en que segundos lo quiere agregar.
    Pide file path del sonido a agregar. 
    Devuelve el objeto de audio del set final con los sonidos agregados."""
    while True:
        try:
            path_sample = Path(input(f"File path: "))
            if path_sample.is_file():
                break  # Salir del bucle si la ruta es válida
            else:
                print(f"Invalid file path. Try again.")
        except:
            print(f"Invalid path, try again")
    audio_sample = AudioSegment.from_file(path_sample)
    n = 0
    for _ in range(q_overlay):
        audio_final = audio_final.overlay(audio_sample, position = segundos[n]*1000, gain_during_overlay=-6)
        n +=1
    return audio_final


def overlay_prompt(duraciondjsetensegundos):
    """Argumentos: Duracion en segundos del set.
    Pregunta si se quiere agregar, cuantos y en que segundos. 
    Deuvelve las respuestas, un string, un int y una lista"""
    while True:
        try:
            yesno_overlay = input((f"Do you want to overlay a DJ sound signature? ")).lower()
            if yesno_overlay == "yes":
                while True:
                    try:
                        q_overlay = int(input(f"How many overlays do you want? (5 max): "))
                        if 0 <= q_overlay <= 5:
                            sec_list = []
                            intentoscorrectos = 0
                            for _ in range(q_overlay):
                                while intentoscorrectos < q_overlay:
                                    try:
                                        secs_overlay = int(input(f"When? Express in seconds: "))
                                        if secs_overlay <= duraciondjsetensegundos and secs_overlay > 0:
                                            sec_list.append(secs_overlay)
                                            intentoscorrectos += 1
                                    except:
                                        print(f"Invalid number, try again")
                            return yesno_overlay, q_overlay, sec_list
                        else:
                            print(f"Invalid number, try a number between 0 and 5")
                    except:
                        print(f"Invalid number, try a number between 0 and 5")
            elif yesno_overlay == "no":
                break
            else:
                print(f"Invalid answer, try again with yes or no")
                continue
        except:
            print(f"Invalid answer, try again with yes or no")


def main():
    #MENSAJE DE BIENVENIDA
    print(welcome_message())
    #MENSAJE DE INFORMACION
    print(info())
    #OBTENGO LINK DEL PRIMER TRACK
    while True:
        try:
            first_track_link = search_first_track()
            first_track_file = download_track(first_track_link)
            break
        except:
            print("Cant add first track")
    #SUMANDO Y MEZCLANDO TRACKS
    set = loop_tracks(first_track_file)
    #DURACION DEL SET
    duracion_djset = duracion_set(set)
    print(f"Your DJ Set its {duracion_djset[0]} mins and {duracion_djset[1]} secs long. Expressed in secs its {duracion_djset[2]} secs")
    #PREGUNTA SI QUEREMOS AGREGAR DJ SOUNDS.
    try:
        yesno, q_over, sec_list = overlay_prompt(duracion_djset[2])
        if yesno == "yes":
            set = overlay_sounds(set, q_over, sec_list)
    except:   
        pass
    #EXPORTAR SET FINAL
    export(set)


if __name__ == "__main__":
    main ()










