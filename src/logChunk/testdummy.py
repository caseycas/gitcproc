      if(curLogChunk.header == ""): #If there is an existing chunk to parse
        #self.processLastChunk(patchObj, curLogChunk)
        if Util.DEBUG == 1: 
          print("Resetting.")
        #curLogChunk.reset()

        temp_func   = line.split("@@ ")
      #print temp_func
        if len(temp_func) <= 2:
        #method name does not exist
            method_name = "NA"
        else:
            temp_func = temp_func[-1]
            curLogChunk.addToText(temp_func.split(" ")[-1])
            if '(' in temp_func:
                temp_func   = temp_func.rsplit('(')[0].strip()
          #print(temp_func)
          #print(temp_func.split(" "))
                method_name = temp_func.split(" ")[-1]
          #print("NAME!" + method_name)
            else:
          #not a traditional method, contains other signature
                method_name = temp_func

