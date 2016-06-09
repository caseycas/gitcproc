import sys
import unittest
import logChunk
from chunkingConstants import *

sys.path.append("../util")

import Util
from Util import ConfigInfo

class logChunktest(unittest.TestCase):

    def readHelper(self,filename):
        inf =open(filename,"r")
        text=""
        for line in inf:
            text+=line

        return text


    def debugFunctions(self, funcList):
        print("===========================================")
        for func in funcList:
            print(func.method)
            print(func.start)
            print(func.end)
            print(func.total_add)
            print(func.total_del)
            print(func.keywordDictionary)           
        print("===========================================")


    def setUp(self):
        self.keyword1 = ["wtc/Assertions.h","excluded","single"]
        self.keyword2 = ["ut_ad","included","single"]
        self.keyword3 = ["try","Included","BLOCK"]
        self.keyword4 = ["for","excludeD","block"]
        self.keyword5 = ["ut_ad included single"]
        self.keyword6 = ["printf(format","str)","included","single"]
        self.keyword7 = ["printf(format, str)","included","single"]
        self.keyword8 = ["assert","incuded","single"]
        self.keyword9 = ["assert","included","lock"]


        self.method1 = "static void blarg() {"
        self.method2 = "int more(int stuff) {"
        self.method3 = "ccv_string * getStuff (int[] stuffToGet) {"
        self.method4 = "int add2to3(int (*functionPtr)(int, int)) {"
        self.method5 = "public static void other(int one, int (*functionPtr)(int, int)) {"
        self.method6 = "static void\n multiline(\n int arg1, string arg2\n) {"
        self.method7 = "int lotsOfSpace     (int stuff) {"
        self.method8 = "                .matrix = {"
        self.method9 = "ccv_string* getStuff (int[] stuffToGet) {"
        self.method10 = "ccv_string *getStuff (int[] stuffToGet) {"
        self.method11 = "void NdbBlob::getBlobEvent(NdbEventImpl& be, const NdbEventImpl* e, const NdbColumnImpl* c) {"
        self.method12 = "bool Repair_mrg_table_error_handler::handle_condition(THD *,uint sql_errno,const char*, MYSQL_ERROR::enum_warning_level level,const char*,MYSQL_ERROR ** cond_hdl) {"
        self.method13 = "(_log2) += 1;  static int CeilingLog2(unsigned int i) {"
        #self.method14 = "(STATEMENT_CONSTRUCTOR_BASE_PARAMETERS, ExpressionPtr exp)   : Statement(STATEMENT_CONSTRUCTOR_BASE_PARAMETER_VALUES),     m_exp(exp) {"
        self.method15 = "static JSC::UString& globalExceptionString(){"
        self.method16 = "(jint) AWT_WINDOW_LOST_FOCUS, (jint) AWT_WINDOW_DEACTIVATED,  static gboolean window_focus_in_cb (GtkWidget * widget, GdkEventFocus *event, jobject peer) {"
        self.method17 = "LinuxPtraceDumper dumper(getpid()); }  TEST(LinuxPtraceDumperTest, FindMappings) {"
        self.method18 = "endif  defined(HAVE_ALTIVEC)   include  elif defined(HAVE_SSE2)   include  endif   ONLY64 inline static int idxof(int i) {"
        self.method19 = "#define UNUSED_VARIABLE(x) (void)(x) const char *sfmt_get_idstring(sfmt_t * sfmt) {"
        self.method20 = "static av_always_inline void hl_motion_420(H264Context *h, uint8_t *dest_y, uint8_t *dest_cb, uint8_t *dest_cr,            qpel_mc_func (*qpix_put)[16], h264_chroma_mc_func (*chroma_put),       qpel_mc_func (*qpix_avg)[16], h264_chroma_mc_func (*chroma_avg),            h264_weight_func *weight_op, h264_biweight_func *weight_avg,             int pixel_shift) {"
        self.method21 = "        for (j = 0; j < i; j++)             if (!memcmp(h->pps.scaling_matrix8[j], h->pps.scaling_matrix8[i],                         64 * sizeof(uint8_t))) {"
        self.method22 = " c_type jl_unbox_##j_type(jl_value_t *v)  {"
        self.method23 = "auto f = via(&x).then([]{"

        c_info = ConfigInfo("../util/sample_conf.ini")

        self.testChunk = logChunk.logChunk("", "C++",c_info)
        self.testChunk_C = logChunk.logChunk("", "C",c_info)

        self.javaMethod1 = "public static Intent createIntent(Context context, String username, String password) {"
        self.javaMethod2 = " public <V> V post(final String uri, final Object params, final Type type) \n throws IOException {"
        self.javaMethod3 = "public static Intent createIntent(final Collection<? extends Issue> issues,\n final Repository repository, final int position) {"
        self.javaMethod4 = "@Override \n public List<User> run(Account account) throws Exception {"
        self.javaMethod5 = "private JClass typeBoundsToJClass(GeneratedClassHolder holder, List<? extends TypeMirror> bounds, Map<String, TypeMirror> actualTypes) {"
        self.javaMethod6 = " public JMethod implementMethod(GeneratedClassHolder holder, List<ExecutableElement> methods, String methodName, String returnType, String... parameterTypes) {"


        #Read in the single tests
        self.chunk1 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk1.txt"), "C++", c_info) #Check C++
        self.chunk2 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk2.txt"), "C", c_info) #Check C
        self.chunk3 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk3.txt"), "C++", c_info) #Check C++
        #self.chunk4 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk4.txt")) #Nope
        #self.chunk5 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk5.txt")) #Nope
        self.chunk6 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk6.txt"), "C++", c_info) #Check C++
        self.chunk7 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk7.txt"), "C++", c_info) #Check C++
        self.chunk8 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk8.txt"), "C++", c_info) #Check C
        self.chunk9 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk9.txt"), "C++", c_info) #Check C++
        self.chunk10 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk10.txt"), "C++", c_info) #Check C++
        self.chunk11 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk11.txt"), "C++", c_info) #Check C++
        self.chunk12 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk12.txt"), "C++", c_info) #Check C++
        self.chunk13 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk13.txt"), "C++", c_info) #Check C++
        self.chunk14 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk14.txt"), "C++",c_info) #Check C++
        self.chunk15 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk15.txt"), "C++",c_info) #Check C++
        #self.chunk16 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk16.txt")) #Nope
        #self.chunk17 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk17.txt")) #Nope
        #self.chunk18 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk18.txt")) #Nope
        #self.chunk19 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk19.txt")) #Nope
        #self.chunk20 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk20.txt")) #Nope
        self.chunk21 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk21.txt"), "C++",c_info) #Check C++ 
        self.chunk22 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk22.txt"), "C++",c_info) #Check C++
        self.chunk23 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk23.txt"), "C++",c_info) #Check C++
        self.chunk24 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk24.txt"), "C++",c_info) #Check C++
        self.chunk25 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk25.txt"), "C",c_info) #Check C
        #self.chunk26 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk26.txt")) #Nope
        self.chunk27 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk27.txt"), "C",c_info) #Check C
        #self.chunk28 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk28.txt")) #Nope
        self.chunk29 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk29.txt"), "C",c_info) #Check C
        #self.chunk30 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk30.txt")) #Maybe?
        self.chunk31 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk31.txt"), "C++",c_info) #Check C++
        self.chunk32 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk32.txt"), "C++",c_info) #Check C++
        self.chunk33 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk33.txt"), "C++",c_info) #Check C++
        #self.chunk34 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk34.txt")) #Nope
        self.chunk35 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk35.txt"), "C",c_info) #Check C
        self.chunk36 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk36.txt"), "C++",c_info) #Check C++
        self.chunk37 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk37.txt"), "C++",c_info) #Check C++
        self.chunk38 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk38.txt"), "C++",c_info) #Check C++
        self.chunk39 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk39.txt"), "C",c_info) #C
        self.chunk40 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk40.txt"), "C",c_info) #Check C
        self.chunk41 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk41.txt"), "C++",c_info) #Check C++
        self.chunk42 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk42.txt"), "C++",c_info) # C++
        self.chunk43 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk43.txt"), "C",c_info) #Check C
        self.chunk44 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk44.txt"), "C++",c_info) # C++
        self.chunk45 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk45.txt"), "C++",c_info) # C++ 
        self.chunk46 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk46.txt"), "C++",c_info) # C++
        self.chunk47 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk47.txt"), "C++",c_info) # C++
        self.chunk48 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk48.txt"), "C++",c_info) # C++
        self.chunk49 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk49.txt"), "C++",c_info) # C++
        self.chunk50 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk50.txt"), "C",c_info) # C
        self.chunk51 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk51.txt"), "C++",c_info)
        self.chunk52 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk52.txt"), "C++",c_info)
        self.chunk53 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk53.txt"), "C++",c_info)
        self.chunk54 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk54.txt"), "C++",c_info)
        self.chunk55 = logChunk.logChunk(self.readHelper("testfiles/Single/testChunk55.txt"), "C++",c_info)





    def test_KeywordValidityCheck(self):
        self.assertTrue(self.testChunk.keywordValidityCheck(self.keyword1))
        self.assertTrue(self.testChunk.keywordValidityCheck(self.keyword2))
        self.assertTrue(self.testChunk.keywordValidityCheck(self.keyword3))
        self.assertTrue(self.testChunk.keywordValidityCheck(self.keyword4))
        self.assertFalse(self.testChunk.keywordValidityCheck(self.keyword5))
        self.assertFalse(self.testChunk.keywordValidityCheck(self.keyword6))
        self.assertTrue(self.testChunk.keywordValidityCheck(self.keyword7))
        self.assertFalse(self.testChunk.keywordValidityCheck(self.keyword8))
        self.assertFalse(self.testChunk.keywordValidityCheck(self.keyword9))



    def test_FunctionNameParse(self):
        temp = self.testChunk.langSwitch.parseFunctionName(self.method1)
        self.assertTrue(temp == "blarg", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method2)
        self.assertTrue(temp == "more", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method3)
        self.assertTrue(temp == "getStuff", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method4)
        self.assertTrue(temp == "add2to3", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method5)
        self.assertTrue(temp == "other", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method6)
        self.assertTrue(temp == "multiline", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method7)
        self.assertTrue(temp == "lotsOfSpace", "Actual: " + temp)

        try:
            temp = self.testChunk.langSwitch.parseFunctionName(self.method8)
            #self.assertTrue(temp == "", "Actual: " + temp)
        except ValueError:
            self.assertTrue(True)

        temp = self.testChunk.langSwitch.parseFunctionName(self.method13)
        self.assertTrue(temp == "CeilingLog2", "Actual: " + temp)
        #print(self.testChunk.getFunctionPattern(self.method14))
        #temp = self.testChunk.parseFunctionName(self.testChunk.getFunctionPattern(self.method14))
        #self.assertTrue(temp == "m_exp", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method16)
        self.assertTrue(temp == "window_focus_in_cb", "Actual: " + temp)

        temp = self.testChunk.langSwitch.parseFunctionName(self.method18)
        self.assertTrue(temp == "idxof", "Actual: " + temp)
        temp = self.testChunk.langSwitch.parseFunctionName(self.method20)
        self.assertTrue(temp == "hl_motion_420", "Actual: " + temp)

    def test_isClassDef(self):
        self.assertTrue(self.testChunk.isClassDef("class A {"))
        self.assertTrue(self.testChunk.isClassDef("template <class T> class calc {"))
        self.assertTrue(self.testChunk.isClassDef("template <class T> class calc : public superclass {"))
        self.assertFalse(self.testChunk.isClassDef("template <class T> T mypair<T>::getmax () {"))
        self.assertFalse(self.testChunk.isClassDef("template < class T > T mypair<T>::getmax () {"))
        self.assertFalse(self.testChunk.isClassDef("Class *cls = *clsh;       while (cls) {"))
        self.assertTrue(self.testChunk.isClassDef("static MDL_global_lock global_lock;  class MDL_object_lock : public MDL_lock {"))

    def test_isConstructorOrDestructor(self):
        self.assertTrue(self.testChunk.isConstructorOrDestructor("~StackHelper() {", "stackhelper"))
        self.assertTrue(self.testChunk.isConstructorOrDestructor("WindowProperties(GdkRectangle* geometry, bool toolbarVisible, bool statusbarVisible, bool scrollbarsVisible, bool menubarVisible,                          bool locationbarVisible, bool resizable, bool fullscreen)             : m_isNull(false)             , m_geometry(*geometry)             , m_toolbarVisible(toolbarVisible)             , m_statusbarVisible(statusbarVisible)             , m_scrollbarsVisible(scrollbarsVisible)             , m_menubarVisible(menubarVisible)             , m_locationbarVisible(locationbarVisible)             , m_resizable(resizable)             , m_fullscreen(fullscreen)         {","windowproperties"))
        self.assertTrue(self.testChunk.isConstructorOrDestructorWithList("      UIClientTest()         : m_scriptDialogType(WEBKIT_SCRIPT_DIALOG_ALERT)         , m_scriptDialogConfirmed(true)         , m_allowPermissionRequests(false)         , m_mouseTargetModifiers(0)     {", ["uiclienttest","windowproperties"]))
        self.assertTrue(self.testChunk.isConstructorOrDestructorWithList("Mutex(int spincount=0) : _spincount(spincount) {", "Mutex"))

    def test_isFunction(self):
        self.assertTrue(self.testChunk.isFunction(self.method1))
        self.assertTrue(self.testChunk.isFunction(self.method2))
        self.assertTrue(self.testChunk.isFunction(self.method3))
        self.assertTrue(self.testChunk.isFunction(self.method4))
        self.assertTrue(self.testChunk.isFunction(self.method5))
        self.assertTrue(self.testChunk.isFunction(self.method6))
        self.assertTrue(self.testChunk.isFunction(self.method7))
        self.assertFalse(self.testChunk.isFunction(self.method8))
        self.assertTrue(self.testChunk.isFunction(self.method9))
        self.assertTrue(self.testChunk.isFunction(self.method10))
        self.assertTrue(self.testChunk.isFunction(self.method11))
        self.assertTrue(self.testChunk.isFunction(self.method12))
        self.assertFalse(self.testChunk.isFunction("class Repair_mrg_table_error_handler : public Internal_error_handler{"))
        self.assertFalse(self.testChunk.isFunction("while(1) {"))
        self.assertFalse(self.testChunk.isFunction("else if(1) {"))
        self.assertTrue(self.testChunk.isFunction(self.method13))
        #self.assertFalse(self.testChunk.isFunction(self.method14))
        self.assertTrue(self.testChunk.isFunction(self.method15))
        self.assertTrue(self.testChunk.isFunction(self.method16))
        # self.assertFalse(self.testChunk.isFunction(self.method17))
        self.assertTrue(self.testChunk.isFunction(self.method18))
        self.assertTrue(self.testChunk.isFunction(self.method19))
        self.assertTrue(self.testChunk.isFunction(self.method20))
        #print("---------------------------------------------------")
        #print(self.testChunk.getFunctionPattern(self.method21))
        #print("---------------------------------------------------")
        self.assertFalse(self.testChunk.isFunction(self.method21))
        self.assertTrue(self.testChunk.isFunction(self.method22))
        self.assertFalse(self.testChunk.isFunction(self.method23))
        self.assertFalse(self.testChunk.isFunction(" set_max_autoinc: if (auto_inc <= col_max_value) {"))

    def test_isFuncC(self):
        self.assertTrue(self.testChunk_C.isFunction("ccv_convnet_t* ccv_convnet_new(int use_cwc_accel, ccv_size_t input, ccv_convnet_layer_param_t params[], int count) {"))

    def test_removeComments(self):
        line = "/***********************************************************//**"
        commentFlag = False
        lineType = ADD
        commentType = OTHER
        functionName = ""
        phase = LOOKFORNAME
        fChange = UNMARKED
        (line, lineType, commentFlag, commentType, functionName, fChange) = self.testChunk.removeComments(line, commentFlag, lineType, commentType, functionName, phase)
        self.assertTrue(line == "")
        self.assertTrue(lineType == ADD)
        self.assertTrue(commentFlag == True)
        self.assertTrue(commentType == ADD)
        self.assertTrue(functionName == "")
        self.assertTrue(fChange == TOTALADD)
        line = "Replaces the new column values stored in the update vector to the index entry"
        lineType = ADD
        (line, lineType, commentFlag, commentType, functionName, fChange) = self.testChunk.removeComments(line, commentFlag, lineType, commentType, functionName, phase)
        self.assertTrue(line == "", "Actual: " + line)
        self.assertTrue(lineType == ADD)
        self.assertTrue(commentFlag == True)
        self.assertTrue(commentType == ADD)
        self.assertTrue(functionName == "")
        self.assertTrue(fChange == TOTALADD)

        line = "/*"
        commentFlag = False
        lineType = REMOVE
        commentType = OTHER
        functionName = ""
        phase = LOOKFOREND
        fChange = UNMARKED
        (line, lineType, commentFlag, commentType, functionName, fChange) = self.testChunk.removeComments(line, commentFlag, lineType, commentType, functionName, phase)
        self.assertTrue(line == "")
        self.assertTrue(lineType == REMOVE)
        self.assertTrue(commentFlag == True)
        self.assertTrue(commentType == REMOVE)
        self.assertTrue(functionName == "")
        self.assertTrue(fChange == COMDEL)
        self.assertTrue(phase == LOOKFOREND)
        line = "private void copy(InputStream is, OutputStream os, String encoding, int max) throws IOException{"
        (line, lineType, commentFlag, commentType, functionName, fChange) = self.testChunk.removeComments(line, commentFlag, lineType, commentType, functionName, phase)
        self.assertTrue(line == "")
        self.assertTrue(lineType == REMOVE)
        self.assertTrue(commentFlag == True)
        self.assertTrue(commentType == REMOVE)
        self.assertTrue(functionName == "")
        self.assertTrue(fChange == COMDEL)
        self.assertTrue(phase == LOOKFOREND)
        line = " "
        lineType = OTHER
        (line, lineType, commentFlag, commentType, functionName, fChange) = self.testChunk.removeComments(line, commentFlag, lineType, commentType, functionName, phase)
        self.assertTrue(line == " ")
        self.assertTrue(lineType == ADD)
        self.assertTrue(commentFlag == True)
        self.assertTrue(commentType == REMOVE)
        self.assertTrue(functionName == "")
        self.assertTrue(fChange == UNMARKED)
        self.assertTrue(phase == LOOKFOREND)
        line = "        Object o = null;"
        lineType = OTHER
        (line, lineType, commentFlag, commentType, functionName, fChange) = self.testChunk.removeComments(line, commentFlag, lineType, commentType, functionName, phase)
        self.assertTrue(line == "        Object o = null;")
        self.assertTrue(lineType == ADD)
        self.assertTrue(commentFlag == True)
        self.assertTrue(commentType == REMOVE)
        self.assertTrue(functionName == "")
        self.assertTrue(fChange == UNMARKED)
        self.assertTrue(phase == LOOKFOREND)

    def test_parseText_Single1(self):
        self.chunk1.parseText()
        funcList = self.chunk1.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 4) 
        self.assertTrue(funcList[0].method=="NdbBlob::getBlobEventName")
        self.assertTrue(funcList[0].total_add == 10)
        self.assertTrue(funcList[0].total_del == 0)

        testDict = {'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}

        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method=="NdbBlob::getBlobEventName")
        self.assertTrue(funcList[1].start==19)
        self.assertTrue(funcList[1].end==22)
        self.assertTrue(funcList[1].total_add == 4)
        self.assertTrue(funcList[1].total_del == 0)
        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)


        self.assertTrue(funcList[2].method=="NdbBlob::getBlobEvent")
        self.assertTrue(funcList[2].start==26)
        self.assertTrue(funcList[2].end==60)
        self.assertTrue(funcList[2].total_add == 35)
        self.assertTrue(funcList[2].total_del == 0)
        testDict = {'assert Adds':2, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[2].keywordDictionary)

        self.assertTrue(funcList[3].method==NON_FUNC)

    def test_parseText_Single2(self):
        self.chunk2.parseText()
        funcList = self.chunk2.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)

        self.assertTrue(funcList[0].method=="btr_pcur_release_leaf")
        self.assertTrue(funcList[0].start==13)
        self.assertTrue(funcList[0].end==27)
        self.assertTrue(funcList[0].total_add == 0)
        self.assertTrue(funcList[0].total_del == 15)

        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 1, 'ut_a Adds':0, 'ut_a Dels': 1}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method==NON_FUNC)
        self.assertTrue(funcList[1].total_add == 0)
        self.assertTrue(funcList[1].total_del == 13)


    def test_parseText_Single3(self):
        self.chunk3.parseText()
        funcList = self.chunk3.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 4)
        self.assertTrue(funcList[0].method=="Repair_mrg_table_error_handler")
        self.assertTrue(funcList[0].start==13)
        self.assertTrue(funcList[0].end==13)
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 0)

        testDict = {'assert Adds':1, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method=="safely_trapped_errors")
        self.assertTrue(funcList[1].start==27)
        self.assertTrue(funcList[1].end==42)

        self.assertTrue(funcList[1].total_add == 16)
        self.assertTrue(funcList[1].total_del == 0)

        testDict = {'assert Adds':1, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)


        self.assertTrue(funcList[2].method=="Repair_mrg_table_error_handler::handle_condition")
        self.assertTrue(funcList[2].start==57)
        self.assertTrue(funcList[2].end==67)
        self.assertTrue(funcList[2].total_add == 11)
        self.assertTrue(funcList[2].total_del == 0)

        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[2].keywordDictionary)


        self.assertTrue(funcList[3].method==NON_FUNC)


    def test_parseText_Single6(self):
        self.chunk6.parseText()
        funcList = self.chunk6.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 4)
        self.assertTrue(funcList[0].method ==  "calc<A_Type>::multiply")
        self.assertTrue(funcList[0].start == 8)
        self.assertTrue(funcList[0].end == 10)
        self.assertTrue(funcList[0].total_add == 3)
        self.assertTrue(funcList[0].total_del == 0)
        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)


        self.assertTrue(funcList[1].method ==  "calc<A_Type>::add")
        self.assertTrue(funcList[1].start == 12)
        self.assertTrue(funcList[1].end == 14)
        self.assertTrue(funcList[1].total_add == 3)
        self.assertTrue(funcList[1].total_del == 0)
        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)


        self.assertTrue(funcList[2].method ==  "calc<A_Type>::divide")
        self.assertTrue(funcList[2].start == 16)
        self.assertTrue(funcList[2].end == 19)
        self.assertTrue(funcList[2].total_add == 4)
        self.assertTrue(funcList[2].total_del == 0)
        testDict = {'assert Adds':1, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[2].keywordDictionary)

        self.assertTrue(funcList[3].method ==  NON_FUNC)

    def test_parseText_Single7(self):
        self.chunk7.parseText()
        funcList = self.chunk7.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 16) #Should be 18, but can't find constructor/destructor outside of class
        self.assertTrue(funcList[6].method ==  "CDVDDemuxPVRClient::Abort", "Actual: " + funcList[7].method)

    def test_parseText_Single8(self):
        self.chunk8.parseText()
        funcList = self.chunk8.functions
        self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 4)

        self.assertTrue(funcList[0].method ==  "GetHelperBinary")
        self.assertTrue(funcList[0].start == 62)
        self.assertTrue(funcList[0].end == 77)
        self.assertTrue(funcList[0].total_add == 16)
        self.assertTrue(funcList[0].total_del == 0)
        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method ==  "StackHelper")
        self.assertTrue(funcList[1].start == 113)
        self.assertTrue(funcList[1].end == 113)
        self.assertTrue(funcList[1].total_add == 1)
        self.assertTrue(funcList[1].total_del == 0)
        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)

        self.assertTrue(funcList[2].method ==  "~StackHelper")
        self.assertTrue(funcList[2].start == 114)
        self.assertTrue(funcList[2].end == 117)
        self.assertTrue(funcList[2].total_add == 4)
        self.assertTrue(funcList[2].total_del == 0)
        testDict = {'assert Adds':0, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[2].keywordDictionary)

        self.assertTrue(funcList[3].method ==  NON_FUNC)
        self.assertTrue(funcList[3].start == 0)
        self.assertTrue(funcList[3].end == 0)
        testDict = {'assert Adds':32, 'assert Dels': 0, 'ut_ad Adds':0, 'ut_ad Dels': 0, 'ut_a Adds':0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[3].keywordDictionary)

    def test_parseText_Single9(self):
        self.chunk9.parseText()

        funcList = self.chunk9.functions
        # self.debugFunctions(funcList)
        #Can't find constructors or destructors outside of classes
        self.assertTrue(len(funcList) == 20)

        self.assertTrue(funcList[6].method ==  "CRuntimeMethod")
        self.assertTrue(funcList[6].start == 119)
        self.assertTrue(funcList[6].end == 121)
        self.assertTrue(funcList[6].total_add == 3)
        self.assertTrue(funcList[6].total_del == 0)
        testDict = { 'ut_ad Adds': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Dels': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[6].keywordDictionary)

    def test_parseText_Single10(self):
        self.chunk10.parseText()
        funcList = self.chunk10.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 7)

        self.assertTrue(funcList[3].method ==  "FreeArenaList")
        self.assertTrue(funcList[3].start == 203)
        self.assertTrue(funcList[3].end == 246)
        self.assertTrue(funcList[3].total_add == 44)
        self.assertTrue(funcList[3].total_del == 0)
        testDict = { 'ut_ad Adds': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Dels': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[3].keywordDictionary)

        self.assertTrue(funcList[6].method ==  NON_FUNC)

    def test_parseText_Single11(self):
        self.chunk11.parseText()
        funcList = self.chunk11.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 6)

        self.assertTrue(funcList[4].method ==  "parseArgs")
        self.assertTrue(funcList[4].start == 81)
        self.assertTrue(funcList[4].end == 199)
        self.assertTrue(funcList[4].total_add == 118)
        self.assertTrue(funcList[4].total_del == 0)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[4].keywordDictionary)

        self.assertTrue(funcList[5].method ==  NON_FUNC)


    def test_parseText_Single12(self):
        self.chunk12.parseText()
        funcList = self.chunk12.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 4)

        self.assertTrue(funcList[1].method ==  "mbfl_buffer_converter_delete")
        self.assertTrue(funcList[1].start == 173)
        self.assertTrue(funcList[1].end == 184)
        self.assertTrue(funcList[1].total_add == 12)
        self.assertTrue(funcList[1].total_del == 0)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)

        self.assertTrue(funcList[3].method ==  NON_FUNC)

    def test_parseText_Single13(self):
        self.chunk13.parseText() #Broken like 2 is
        funcList = self.chunk13.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 3)

        self.assertTrue(funcList[0].method ==  "ClassCache::hashKey")
        self.assertTrue(funcList[0].start == 6)
        self.assertTrue(funcList[0].end == 8)
        self.assertTrue(funcList[0].total_add == 0)
        self.assertTrue(funcList[0].total_del == 3)
        #self.assertTrue(len(funcList[0].assertionList) == 0)

        self.assertTrue(funcList[1].method ==  "ClassCache::lookup")
        self.assertTrue(funcList[1].start == 13)
        self.assertTrue(funcList[1].end == 41)
        self.assertTrue(funcList[1].total_add == 0)
        self.assertTrue(funcList[1].total_del == 29)
        #self.assertTrue(len(funcList[1].assertionList) == 0)

        self.assertTrue(funcList[2].method ==  NON_FUNC)

    def test_parseText_Single14(self):
        self.chunk14.parseText()
        funcList = self.chunk14.functions
        # self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)

        self.assertTrue(funcList[0].method ==  "getDynLocType")
        self.assertTrue(funcList[0].start == 8)
        self.assertTrue(funcList[0].end == 241)

        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 15, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method ==  NON_FUNC)

    def test_parseText_Single15(self):
        self.chunk15.parseText()
        # funcList = self.chunk15.functions
        # #self.debugFunctions(funcList)

    def test_parseText_Single21(self):
        self.chunk21.parseText()
        funcList = self.chunk21.functions
        #self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method ==  "MDL_object_lock")

        self.assertTrue(funcList[1].method ==  NON_FUNC)
        self.assertTrue(funcList[1].total_add == 16)
        self.assertTrue(funcList[1].total_del == 1)

    def test_parseText_Single22(self):
        self.chunk22.parseText()
        funcList = self.chunk22.functions
        self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 7) #Can't get the last one b/c constructor out of context
        self.assertTrue(funcList[0].method ==  "MDL_map::init")
        self.assertTrue(funcList[1].method ==  "MDL_map::destroy")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)

        self.assertTrue(funcList[2].method ==  "MDL_map::find_or_insert")
        self.assertTrue(funcList[3].method ==  "MDL_map::find")
        self.assertTrue(funcList[4].method ==  "MDL_map::move_from_hash_to_lock_mutex")

        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 2, 'ut_a Dels': 0}
        self.assertTrue(testDict,funcList[4].keywordDictionary)
        self.assertTrue(funcList[5].method ==  "MDL_map::remove")

        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[5].keywordDictionary)

        self.assertTrue(funcList[6].method ==  NON_FUNC)

   
    def test_parseText_Single23(self):
        self.chunk23.parseText()
        funcList = self.chunk23.functions
        self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 3)

        self.assertTrue(funcList[0].method ==  "MDL_ticket::has_pending_conflicting_lock_impl")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 2, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)
        self.assertTrue(funcList[1].method ==  "MDL_ticket::has_pending_conflicting_lock") #Name not in + or -
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)
        self.assertTrue(funcList[2].method ==  NON_FUNC)

    def test_parseText_Single24(self):
        self.chunk24.parseText()
        funcList = self.chunk24.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 25)

        self.assertTrue(funcList[16].method ==  "*get_date_time_format_str")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[16].keywordDictionary)

    def test_parseText_Single25(self):
        self.chunk25.parseText()
        funcList = self.chunk25.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 5)

        self.assertTrue(funcList[2].method ==  "row_upd_index_replace_new_col_vals_index_pos")
        testDict = { 'ut_ad Adds': 1, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[2].keywordDictionary)


    def test_parseText_Single27(self):
        self.chunk27.parseText()
        funcList = self.chunk27.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 31)

    def test_parseText_Single29(self):
        self.chunk29.parseText()
        funcList = self.chunk29.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 16)

        self.assertTrue(funcList[0].method == "idxof")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method == "idxof")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)

        self.assertTrue(funcList[7].method == "*sfmt_get_idstring")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[7].keywordDictionary)

        self.assertTrue(funcList[11].method ==  "sfmt_fill_array32")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 3, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[11].keywordDictionary)

        self.assertTrue(funcList[12].method ==  "sfmt_fill_array64")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 3, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[12].keywordDictionary)


    def test_parseText_Single31(self):
        self.chunk31.parseText() 
        funcList = self.chunk31.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)

        self.assertTrue(funcList[0].method ==  "smp_callin")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 1, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method ==  NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 1, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)

    def test_parseText_Single32(self):
        self.chunk32.parseText()
        funcList = self.chunk32.functions
        # #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 11)

        self.assertTrue(funcList[1].method ==  "h264_er_decode_mb")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)


        self.assertTrue(funcList[7].method ==  "alloc_picture")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 2, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[7].keywordDictionary)

        self.assertTrue(funcList[10].method ==  NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[10].keywordDictionary)


    def test_parseText_Single33(self):
        self.chunk33.parseText()
        #Problems:
        #Also, get a false assert? when we have a function name named assert.
        funcList = self.chunk33.functions
        self.debugFunctions(funcList)
        # print("Length: " + str(len(funcList)))
        self.assertTrue(len(funcList) == 24)

        self.assertTrue(funcList[23].method ==  NON_FUNC)

    def test_parseText_Single35(self):
        self.chunk35.parseText()
        funcList = self.chunk35.functions
        self.debugFunctions(funcList)

        self.assertTrue(funcList[-1].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[-1].keywordDictionary)


    def test_parseText_Single36(self):
        self.chunk36.parseText() 
        funcList = self.chunk36.functions
        #self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 3) # 2 + 1 Mock

        self.assertTrue(funcList[1].method ==  "Patch")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 5, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[1].keywordDictionary)

        self.assertTrue(funcList[2].method ==  NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 1, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict,funcList[2].keywordDictionary)

    def test_parseText_Single37(self):
        self.chunk37.parseText()
        funcList = self.chunk37.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)

        self.assertTrue(funcList[0].method ==  "NamespaceDetails::_alloc")
        self.assertTrue(funcList[0].total_add == 6)
        self.assertTrue(funcList[0].total_del == 3)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 1, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)

    def test_parseText_Single38(self):
        self.chunk38.parseText()
        funcList = self.chunk38.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 5)
        self.assertTrue(funcList[0].method == "mysql_stmt_fetch")
        self.assertTrue(funcList[0].total_add == 6)
        self.assertTrue(funcList[0].total_del == 1)
        self.assertTrue(funcList[1].method ==  "mysql_stmt_reset")
        self.assertTrue(funcList[1].total_add == 6)
        self.assertTrue(funcList[1].total_del == 1)
        self.assertTrue(funcList[2].method ==  "mysql_stmt_close")
        self.assertTrue(funcList[2].total_add == 3)
        self.assertTrue(funcList[2].total_del == 3)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 1, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[2].keywordDictionary)

    def test_parseText_Single40(self):
        self.chunk40.parseText()
        funcList = self.chunk40.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method == "jl_unbox_##j_type")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 2)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 2, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 2, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)

    def test_parseText_Single41(self):
        self.chunk41.parseText()
        funcList = self.chunk41.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 10)
        self.assertTrue(funcList[0].method == "Mutex")
        self.assertTrue(funcList[4].method == "Mutex")
        self.assertTrue(funcList[9].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[9].keywordDictionary)

    def test_parseText_Single42(self):
        self.chunk42.parseText()
        funcList = self.chunk42.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method == "Benchmark<P_parameter>::saveMatlabGraph")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)
        self.assertTrue(funcList[1].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[1].keywordDictionary)

    def test_parseText_Single43(self):
        self.chunk43.parseText()
        funcList = self.chunk43.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method == "incr_flush_list_size_in_bytes")
        testDict = { 'ut_ad Adds': 2, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)
        self.assertTrue(funcList[1].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[1].keywordDictionary)

    def test_parseText_Single44(self):
        self.chunk44.parseText()
        funcList = self.chunk44.functions
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method == "auto_copying_data_provider_t::get_data_into_buffers")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 4, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)
        self.assertTrue(funcList[1].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[1].keywordDictionary)

    def test_parseText_Single45(self): #Not Sure how I want to handle this
        self.chunk45.parseText()
        funcList = self.chunk45.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method == "Int32BinopInputShapeTester")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)
        self.assertTrue(funcList[1].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[1].keywordDictionary)

    def test_parseText_Single46(self): #Not Sure how I want to handle this
        self.chunk46.parseText()
        funcList = self.chunk46.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 3)
        self.assertTrue(funcList[0].method == "QuatF::mulP")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method == "QuatF::mul")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[1].keywordDictionary)

        self.assertTrue(funcList[2].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[2].keywordDictionary)

    def test_parseText_Single47(self): #Not Sure how I want to handle this
        self.chunk47.parseText()
        funcList = self.chunk47.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method == "CCAnimate::initWithAnimation")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 1, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 1, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)

    def test_parseText_Single48(self): #Not Sure how I want to handle this
        self.chunk48.parseText()
        funcList = self.chunk48.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 5)
        self.assertTrue(funcList[0].method == "&=")
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 1, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)

        self.assertTrue(funcList[4].method == NON_FUNC)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[4].keywordDictionary)


    def test_parseText_Single49(self): #Not Sure how I want to handle this
        self.chunk49.parseText()
        funcList = self.chunk49.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method == "ClientInfo::newRequest")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 1)

        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)

        self.assertTrue(funcList[1].method == "ClientInfo::create")
        self.assertTrue(funcList[1].total_add == 1)
        self.assertTrue(funcList[1].total_del == 1)
        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[1].keywordDictionary)


    def test_parseText_Single50(self): #Not Sure how I want to handle this
        self.chunk50.parseText()
        funcList = self.chunk50.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method == "xfs_buf_get")
        self.assertTrue(funcList[0].total_add == 2)
        self.assertTrue(funcList[0].total_del == 7)

        testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        self.assertEqual(testDict, funcList[0].keywordDictionary)


    def test_parseText_Single51(self):
        #This is not a correct parsing case, and I'm not exactly sure why, something to do with
        #changing inheritance statements in C++
        #I don't have time to fix this yet, so I'm adding a test case to make sure it doesn't crash
        #but instead returns a error parse statement
        self.chunk51.parseText()
        funcList = self.chunk51.functions 
        #self.debugFunctions(funcList)

        self.assertTrue(len(funcList) == 1)
        self.assertTrue(funcList[0].method == CHUNK_ERROR)

    def test_parseText_Single52(self): #Not Sure how I want to handle this, this case is part of a larger failing chunk.
        self.chunk52.parseText()
        funcList = self.chunk52.functions 
        #self.debugFunctions(funcList)

    def test_parseText_Single53(self): 
        #This is an old style K&R C function declaration.
        #http://stackoverflow.com/questions/3092006/function-declaration-kr-vs-ansi
        #The syntax is deprecated but still legal.
        #I think trying to capture these may accidently lead to capturing other types of non-functions, 
        #due to the presence of ';'.  I'll throw an issue up for it.
        self.chunk53.parseText()
        funcList = self.chunk53.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 1)
        #Re-enable this later....
        #self.assertTrue(funcList[0].method == "set_offsets_for_label")


    def test_parseText_Single54(self): 
        self.chunk54.parseText()
        funcList = self.chunk54.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 6)
        self.assertTrue(funcList[0].method == "Reset")
        self.assertTrue(funcList[1].method == "EnterCombat")
        self.assertTrue(funcList[2].method == "MoveInLineOfSight")
        self.assertTrue(funcList[3].method == "Reset")
        self.assertTrue(funcList[4].method == "EnterCombat")
        self.assertTrue(funcList[5].method == "MoveInLineOfSight")

    def test_parseText_Single55(self): # Testing our ability to find struct constructors.
        self.chunk55.parseText()
        funcList = self.chunk55.functions 
        #self.debugFunctions(funcList)
        self.assertTrue(len(funcList) == 2)
        self.assertTrue(funcList[0].method == "boss_jaraxxusAI")
        self.assertTrue(funcList[0].total_add == 1)
        self.assertTrue(funcList[0].total_del == 1)

        self.assertTrue(funcList[1].method == NON_FUNC)
        self.assertTrue(funcList[1].total_add == 1)
        self.assertTrue(funcList[1].total_del == 1)



#This olds test cases that no longer apply under the new spec
    #def test_parseText_SingleNA(self):
        # #self.chunk4.parseText()
        # #self.chunk5.parseText()
        # #self.chunk16.parseText()
        # #self.chunk17.parseText()
        # #self.chunk18.parseText()
        # #self.chunk19.parseText()
        # #self.chunk20.parseText()
        # #self.chunk26.parseText()
        # #self.chunk28.parseText()
        # #self.chunk30.parseText()
        # #self.chunk34.parseText()

        # funcList = self.chunk4.functions
        # #self.debugFunctions(funcList)
        # self.assertTrue(len(funcList) == 0)

        # funcList = self.chunk5.functions
        # #self.debugFunctions(funcList)
        # self.assertTrue(len(funcList) == 0)
        # self.assertTrue(self.chunk5.total_add == 20)
        # self.assertTrue(self.chunk5.total_del == 1)

        # funcList = self.chunk16.functions
        # #self.debugFunctions(funcList)

        # funcList = self.chunk17.functions
        # #self.debugFunctions(funcList)

        # funcList = self.chunk18.functions
        # #self.debugFunctions(funcList)

        # #Bug: Can't see a return type, but at least this no longer crashes.
        # #self.assertTrue(len(funcList) == 1)
        # #self.assertTrue(funcList[0].method ==  "build_call_n")

        # funcList = self.chunk19.functions
        # #self.debugFunctions(funcList)
        # #print("FUNCTIONS")
        # #print(funcList)
        # self.assertTrue(len(funcList) == 2)

        # self.assertTrue(funcList[0].method ==  "window_focus_in_cb")

        # self.assertTrue(funcList[1].method ==  "window_focus_out_cb")
        # self.assertTrue(funcList[1].start == 23)
        # self.assertTrue(funcList[1].end == 29)

        # funcList = self.chunk20.functions
        # #self.debugFunctions(funcList)
        # #print("FUNCTIONS")
        # #print(funcList)
        # self.assertTrue(len(funcList) == 4)
        # self.assertTrue(funcList[0].method ==  "has_pending_exclusive_lock")
        # self.assertTrue(funcList[1].method ==  "~MDL_lock")
        # self.assertTrue(funcList[2].method ==  "MDL_global_lock")
        # self.assertTrue(funcList[3].method ==  "is_empty")

        # funcList = self.chunk26.functions
        # #self.debugFunctions(funcList)
        # self.assertTrue(len(funcList) == 1)
        # self.assertTrue(funcList[0].method ==  "NO_FUNC_CONTEXT")
        # self.assertTrue(len(funcList[0].assertionList) == 8)

        #funcList = self.chunk28.functions
        #self.debugFunctions(funcList)

        #self.assertTrue(len(funcList) == 6)

        #funcList = self.chunk30.functions
        #self.debugFunctions(funcList)
        #self.assertTrue(len(funcList) == 2)

        #self.assertTrue(funcList[0].method ==  "_ccv_rgb_to_yuv")
        #testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 0, 'ut_a Dels': 0}
        #self.assertTrue(testDict,funcList[0].keywordDictionary)
        #self.assertTrue(len(funcList[0].assertionList) == 0)

        #self.assertTrue(funcList[1].method ==  "ccv_color_transform")
        #testDict = { 'ut_ad Adds': 0, 'assert Dels': 0, 'ut_ad Dels': 0, 'ut_a Adds': 0, 'assert Adds': 2, 'ut_a Dels': 0}
        #self.assertTrue(testDict,funcList[1].keywordDictionary)
        #self.assertTrue(len(funcList[1].assertionList) == 2)

        #This one was always alright, I just didn't read it correctly...
        #funcList = self.chunk34.functions
        #self.debugFunctions(funcList)
        #self.assertTrue(len(funcList) == 0)



if __name__=="__main__":
    unittest.main()
