; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Map" = type {i64*, i64*, i64, i64}
%"Set" = type {i64*, i64, i64}
%"Deque" = type {i64*, i64, i64, i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"GC_malloc"(i64 %".1")

declare void @"GC_init"()

declare void @"GC_free"(i8* %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

declare i8* @"strcat"(i8* %".1", i8* %".2")

declare i64 @"strlen"(i8* %".1")

declare i32 @"snprintf"(i8* %".1", i64 %".2", i8* %".3", ...)

declare i8* @"strstr"(i8* %".1", i8* %".2")

declare i32 @"strncmp"(i8* %".1", i8* %".2", i64 %".3")

declare i64 @"atoi"(i8* %".1")

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i8* @"strncpy"(i8* %".1", i8* %".2", i64 %".3")

@"stdin" = external global i8*
@"stdout" = external global i8*
@"stderr" = external global i8*
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [23 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"new_map_call" = call %"Map"* @"new_map"()
  %"m" = alloca %"Map"*
  store %"Map"* %"new_map_call", %"Map"** %"m"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 100
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"m_load" = load %"Map"*, %"Map"** %"m"
  %"i_load.1" = load i64, i64* %"i"
  %"i_load.2" = load i64, i64* %"i"
  %"mul" = mul i64 %"i_load.2", 10
  call void @"Map_insert"(%"Map"* %"m_load", i64 %"i_load.1", i64 %"mul")
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %".16" = bitcast [6 x i8]* @"str_3" to i8*
  %".17" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %"m_load.1" = load %"Map"*, %"Map"** %"m"
  %".18" = getelementptr %"Map", %"Map"* %"m_load.1", i32 0, i32 2
  %"size_load" = load i64, i64* %".18"
  %".19" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"size_load")
  %".21" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [8 x i8]* @"str_8" to i8*
  %".23" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"m_load.2" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call" = call i64 @"Map_get"(%"Map"* %"m_load.2", i64 0)
  %".24" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"Map_get_call")
  %".26" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [9 x i8]* @"str_13" to i8*
  %".28" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %"m_load.3" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.1" = call i64 @"Map_get"(%"Map"* %"m_load.3", i64 50)
  %".29" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".30", i64 %"Map_get_call.1")
  %".31" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [9 x i8]* @"str_18" to i8*
  %".33" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %"m_load.4" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.2" = call i64 @"Map_get"(%"Map"* %"m_load.4", i64 99)
  %".34" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".35", i64 %"Map_get_call.2")
  %".36" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %".37" = bitcast [10 x i8]* @"str_23" to i8*
  %".38" = bitcast [3 x i8]* @"str_24" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".38", i8* %".37")
  %"m_load.5" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.3" = call i64 @"Map_get"(%"Map"* %"m_load.5", i64 100)
  %".39" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".39")
  %".40" = bitcast [4 x i8]* @"str_26" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".40", i64 %"Map_get_call.3")
  %".41" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".41")
  %".42" = bitcast [14 x i8]* @"str_28" to i8*
  %".43" = bitcast [3 x i8]* @"str_29" to i8*
  %"print_call.11" = call i32 (i8*, ...) @"printf"(i8* %".43", i8* %".42")
  %"m_load.6" = load %"Map"*, %"Map"** %"m"
  %"Map_contains_call" = call i64 @"Map_contains"(%"Map"* %"m_load.6", i64 42)
  %".44" = bitcast [2 x i8]* @"str_30" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".44")
  %".45" = bitcast [4 x i8]* @"str_31" to i8*
  %"print_call.12" = call i32 (i8*, ...) @"printf"(i8* %".45", i64 %"Map_contains_call")
  %".46" = bitcast [2 x i8]* @"str_32" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".46")
  %".47" = bitcast [15 x i8]* @"str_33" to i8*
  %".48" = bitcast [3 x i8]* @"str_34" to i8*
  %"print_call.13" = call i32 (i8*, ...) @"printf"(i8* %".48", i8* %".47")
  %"m_load.7" = load %"Map"*, %"Map"** %"m"
  %"Map_contains_call.1" = call i64 @"Map_contains"(%"Map"* %"m_load.7", i64 100)
  %".49" = bitcast [2 x i8]* @"str_35" to i8*
  %"print_sep.6" = call i32 (i8*, ...) @"printf"(i8* %".49")
  %".50" = bitcast [4 x i8]* @"str_36" to i8*
  %"print_call.14" = call i32 (i8*, ...) @"printf"(i8* %".50", i64 %"Map_contains_call.1")
  %".51" = bitcast [2 x i8]* @"str_37" to i8*
  %"print_nl.7" = call i32 (i8*, ...) @"printf"(i8* %".51")
  %".52" = bitcast [34 x i8]* @"str_38" to i8*
  %".53" = bitcast [3 x i8]* @"str_39" to i8*
  %"print_call.15" = call i32 (i8*, ...) @"printf"(i8* %".53", i8* %".52")
  %".54" = bitcast [2 x i8]* @"str_40" to i8*
  %"print_nl.8" = call i32 (i8*, ...) @"printf"(i8* %".54")
  %"m_load.8" = load %"Map"*, %"Map"** %"m"
  %"Map_remove_call" = call i64 @"Map_remove"(%"Map"* %"m_load.8", i64 50)
  %".55" = bitcast [14 x i8]* @"str_41" to i8*
  %".56" = bitcast [3 x i8]* @"str_42" to i8*
  %"print_call.16" = call i32 (i8*, ...) @"printf"(i8* %".56", i8* %".55")
  %"m_load.9" = load %"Map"*, %"Map"** %"m"
  %"Map_contains_call.2" = call i64 @"Map_contains"(%"Map"* %"m_load.9", i64 50)
  %".57" = bitcast [2 x i8]* @"str_43" to i8*
  %"print_sep.7" = call i32 (i8*, ...) @"printf"(i8* %".57")
  %".58" = bitcast [4 x i8]* @"str_44" to i8*
  %"print_call.17" = call i32 (i8*, ...) @"printf"(i8* %".58", i64 %"Map_contains_call.2")
  %".59" = bitcast [2 x i8]* @"str_45" to i8*
  %"print_nl.9" = call i32 (i8*, ...) @"printf"(i8* %".59")
  %".60" = bitcast [9 x i8]* @"str_46" to i8*
  %".61" = bitcast [3 x i8]* @"str_47" to i8*
  %"print_call.18" = call i32 (i8*, ...) @"printf"(i8* %".61", i8* %".60")
  %"m_load.10" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.4" = call i64 @"Map_get"(%"Map"* %"m_load.10", i64 50)
  %".62" = bitcast [2 x i8]* @"str_48" to i8*
  %"print_sep.8" = call i32 (i8*, ...) @"printf"(i8* %".62")
  %".63" = bitcast [4 x i8]* @"str_49" to i8*
  %"print_call.19" = call i32 (i8*, ...) @"printf"(i8* %".63", i64 %"Map_get_call.4")
  %".64" = bitcast [2 x i8]* @"str_50" to i8*
  %"print_nl.10" = call i32 (i8*, ...) @"printf"(i8* %".64")
  %"m_load.11" = load %"Map"*, %"Map"** %"m"
  call void @"Map_insert"(%"Map"* %"m_load.11", i64 50, i64 5000)
  %".65" = bitcast [9 x i8]* @"str_51" to i8*
  %".66" = bitcast [3 x i8]* @"str_52" to i8*
  %"print_call.20" = call i32 (i8*, ...) @"printf"(i8* %".66", i8* %".65")
  %"m_load.12" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.5" = call i64 @"Map_get"(%"Map"* %"m_load.12", i64 50)
  %".67" = bitcast [2 x i8]* @"str_53" to i8*
  %"print_sep.9" = call i32 (i8*, ...) @"printf"(i8* %".67")
  %".68" = bitcast [4 x i8]* @"str_54" to i8*
  %"print_call.21" = call i32 (i8*, ...) @"printf"(i8* %".68", i64 %"Map_get_call.5")
  %".69" = bitcast [2 x i8]* @"str_55" to i8*
  %"print_nl.11" = call i32 (i8*, ...) @"printf"(i8* %".69")
  %".70" = bitcast [23 x i8]* @"str_56" to i8*
  %".71" = bitcast [3 x i8]* @"str_57" to i8*
  %"print_call.22" = call i32 (i8*, ...) @"printf"(i8* %".71", i8* %".70")
  %".72" = bitcast [2 x i8]* @"str_58" to i8*
  %"print_nl.12" = call i32 (i8*, ...) @"printf"(i8* %".72")
  %"new_set_call" = call %"Set"* @"new_set"()
  %"s" = alloca %"Set"*
  store %"Set"* %"new_set_call", %"Set"** %"s"
  %"j" = alloca i64
  store i64 0, i64* %"j"
  br label %"while_cond.1"
while_cond.1:
  %"j_load" = load i64, i64* %"j"
  %"icmp.1" = icmp slt i64 %"j_load", 100
  br i1 %"icmp.1", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"s_load" = load %"Set"*, %"Set"** %"s"
  %"j_load.1" = load i64, i64* %"j"
  call void @"Set_add"(%"Set"* %"s_load", i64 %"j_load.1")
  %"j_load.2" = load i64, i64* %"j"
  %"add.1" = add i64 %"j_load.2", 1
  store i64 %"add.1", i64* %"j"
  br label %"while_cond.1"
while_end.1:
  %".79" = bitcast [6 x i8]* @"str_59" to i8*
  %".80" = bitcast [3 x i8]* @"str_60" to i8*
  %"print_call.23" = call i32 (i8*, ...) @"printf"(i8* %".80", i8* %".79")
  %"s_load.1" = load %"Set"*, %"Set"** %"s"
  %".81" = getelementptr %"Set", %"Set"* %"s_load.1", i32 0, i32 1
  %"size_load.1" = load i64, i64* %".81"
  %".82" = bitcast [2 x i8]* @"str_61" to i8*
  %"print_sep.10" = call i32 (i8*, ...) @"printf"(i8* %".82")
  %".83" = bitcast [4 x i8]* @"str_62" to i8*
  %"print_call.24" = call i32 (i8*, ...) @"printf"(i8* %".83", i64 %"size_load.1")
  %".84" = bitcast [2 x i8]* @"str_63" to i8*
  %"print_nl.13" = call i32 (i8*, ...) @"printf"(i8* %".84")
  %".85" = bitcast [13 x i8]* @"str_64" to i8*
  %".86" = bitcast [3 x i8]* @"str_65" to i8*
  %"print_call.25" = call i32 (i8*, ...) @"printf"(i8* %".86", i8* %".85")
  %"s_load.2" = load %"Set"*, %"Set"** %"s"
  %"Set_contains_call" = call i64 @"Set_contains"(%"Set"* %"s_load.2", i64 0)
  %".87" = bitcast [2 x i8]* @"str_66" to i8*
  %"print_sep.11" = call i32 (i8*, ...) @"printf"(i8* %".87")
  %".88" = bitcast [4 x i8]* @"str_67" to i8*
  %"print_call.26" = call i32 (i8*, ...) @"printf"(i8* %".88", i64 %"Set_contains_call")
  %".89" = bitcast [2 x i8]* @"str_68" to i8*
  %"print_nl.14" = call i32 (i8*, ...) @"printf"(i8* %".89")
  %".90" = bitcast [14 x i8]* @"str_69" to i8*
  %".91" = bitcast [3 x i8]* @"str_70" to i8*
  %"print_call.27" = call i32 (i8*, ...) @"printf"(i8* %".91", i8* %".90")
  %"s_load.3" = load %"Set"*, %"Set"** %"s"
  %"Set_contains_call.1" = call i64 @"Set_contains"(%"Set"* %"s_load.3", i64 99)
  %".92" = bitcast [2 x i8]* @"str_71" to i8*
  %"print_sep.12" = call i32 (i8*, ...) @"printf"(i8* %".92")
  %".93" = bitcast [4 x i8]* @"str_72" to i8*
  %"print_call.28" = call i32 (i8*, ...) @"printf"(i8* %".93", i64 %"Set_contains_call.1")
  %".94" = bitcast [2 x i8]* @"str_73" to i8*
  %"print_nl.15" = call i32 (i8*, ...) @"printf"(i8* %".94")
  %".95" = bitcast [15 x i8]* @"str_74" to i8*
  %".96" = bitcast [3 x i8]* @"str_75" to i8*
  %"print_call.29" = call i32 (i8*, ...) @"printf"(i8* %".96", i8* %".95")
  %"s_load.4" = load %"Set"*, %"Set"** %"s"
  %"Set_contains_call.2" = call i64 @"Set_contains"(%"Set"* %"s_load.4", i64 100)
  %".97" = bitcast [2 x i8]* @"str_76" to i8*
  %"print_sep.13" = call i32 (i8*, ...) @"printf"(i8* %".97")
  %".98" = bitcast [4 x i8]* @"str_77" to i8*
  %"print_call.30" = call i32 (i8*, ...) @"printf"(i8* %".98", i64 %"Set_contains_call.2")
  %".99" = bitcast [2 x i8]* @"str_78" to i8*
  %"print_nl.16" = call i32 (i8*, ...) @"printf"(i8* %".99")
  %".100" = bitcast [23 x i8]* @"str_79" to i8*
  %".101" = bitcast [3 x i8]* @"str_80" to i8*
  %"print_call.31" = call i32 (i8*, ...) @"printf"(i8* %".101", i8* %".100")
  %".102" = bitcast [2 x i8]* @"str_81" to i8*
  %"print_nl.17" = call i32 (i8*, ...) @"printf"(i8* %".102")
  %"new_deque_call" = call %"Deque"* @"new_deque"()
  %"d" = alloca %"Deque"*
  store %"Deque"* %"new_deque_call", %"Deque"** %"d"
  %"k" = alloca i64
  store i64 0, i64* %"k"
  br label %"while_cond.2"
while_cond.2:
  %"k_load" = load i64, i64* %"k"
  %"icmp.2" = icmp slt i64 %"k_load", 100
  br i1 %"icmp.2", label %"while_body.2", label %"while_end.2"
while_body.2:
  %"d_load" = load %"Deque"*, %"Deque"** %"d"
  %"k_load.1" = load i64, i64* %"k"
  call void @"Deque_push_back"(%"Deque"* %"d_load", i64 %"k_load.1")
  %"k_load.2" = load i64, i64* %"k"
  %"add.2" = add i64 %"k_load.2", 1
  store i64 %"add.2", i64* %"k"
  br label %"while_cond.2"
while_end.2:
  %".109" = bitcast [6 x i8]* @"str_82" to i8*
  %".110" = bitcast [3 x i8]* @"str_83" to i8*
  %"print_call.32" = call i32 (i8*, ...) @"printf"(i8* %".110", i8* %".109")
  %"d_load.1" = load %"Deque"*, %"Deque"** %"d"
  %".111" = getelementptr %"Deque", %"Deque"* %"d_load.1", i32 0, i32 2
  %"size_load.2" = load i64, i64* %".111"
  %".112" = bitcast [2 x i8]* @"str_84" to i8*
  %"print_sep.14" = call i32 (i8*, ...) @"printf"(i8* %".112")
  %".113" = bitcast [4 x i8]* @"str_85" to i8*
  %"print_call.33" = call i32 (i8*, ...) @"printf"(i8* %".113", i64 %"size_load.2")
  %".114" = bitcast [2 x i8]* @"str_86" to i8*
  %"print_nl.18" = call i32 (i8*, ...) @"printf"(i8* %".114")
  %".115" = bitcast [8 x i8]* @"str_87" to i8*
  %".116" = bitcast [3 x i8]* @"str_88" to i8*
  %"print_call.34" = call i32 (i8*, ...) @"printf"(i8* %".116", i8* %".115")
  %"d_load.2" = load %"Deque"*, %"Deque"** %"d"
  %"Deque_get_call" = call i64 @"Deque_get"(%"Deque"* %"d_load.2", i64 0)
  %".117" = bitcast [2 x i8]* @"str_89" to i8*
  %"print_sep.15" = call i32 (i8*, ...) @"printf"(i8* %".117")
  %".118" = bitcast [4 x i8]* @"str_90" to i8*
  %"print_call.35" = call i32 (i8*, ...) @"printf"(i8* %".118", i64 %"Deque_get_call")
  %".119" = bitcast [2 x i8]* @"str_91" to i8*
  %"print_nl.19" = call i32 (i8*, ...) @"printf"(i8* %".119")
  %".120" = bitcast [9 x i8]* @"str_92" to i8*
  %".121" = bitcast [3 x i8]* @"str_93" to i8*
  %"print_call.36" = call i32 (i8*, ...) @"printf"(i8* %".121", i8* %".120")
  %"d_load.3" = load %"Deque"*, %"Deque"** %"d"
  %"Deque_get_call.1" = call i64 @"Deque_get"(%"Deque"* %"d_load.3", i64 50)
  %".122" = bitcast [2 x i8]* @"str_94" to i8*
  %"print_sep.16" = call i32 (i8*, ...) @"printf"(i8* %".122")
  %".123" = bitcast [4 x i8]* @"str_95" to i8*
  %"print_call.37" = call i32 (i8*, ...) @"printf"(i8* %".123", i64 %"Deque_get_call.1")
  %".124" = bitcast [2 x i8]* @"str_96" to i8*
  %"print_nl.20" = call i32 (i8*, ...) @"printf"(i8* %".124")
  %".125" = bitcast [9 x i8]* @"str_97" to i8*
  %".126" = bitcast [3 x i8]* @"str_98" to i8*
  %"print_call.38" = call i32 (i8*, ...) @"printf"(i8* %".126", i8* %".125")
  %"d_load.4" = load %"Deque"*, %"Deque"** %"d"
  %"Deque_get_call.2" = call i64 @"Deque_get"(%"Deque"* %"d_load.4", i64 99)
  %".127" = bitcast [2 x i8]* @"str_99" to i8*
  %"print_sep.17" = call i32 (i8*, ...) @"printf"(i8* %".127")
  %".128" = bitcast [4 x i8]* @"str_100" to i8*
  %"print_call.39" = call i32 (i8*, ...) @"printf"(i8* %".128", i64 %"Deque_get_call.2")
  %".129" = bitcast [2 x i8]* @"str_101" to i8*
  %"print_nl.21" = call i32 (i8*, ...) @"printf"(i8* %".129")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define i64 @"_map_hash"(i64 %".1", i64 %".2")
{
_map_hash_entry:
  %"key" = alloca i64
  store i64 %".1", i64* %"key"
  %"cap" = alloca i64
  store i64 %".2", i64* %"cap"
  br label %"_map_hash_body"
_map_hash_body:
  %"key_load" = load i64, i64* %"key"
  %"cap_load" = load i64, i64* %"cap"
  %"sub" = sub i64 %"cap_load", 1
  %"bitand" = and i64 %"key_load", %"sub"
  ret i64 %"bitand"
}

define void @"Map_rehash"(%"Map"* %".1")
{
Map_rehash_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  br label %"Map_rehash_body"
Map_rehash_body:
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".5" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".5"
  %"old_keys" = alloca i64*
  store i64* %"keys_load", i64** %"old_keys"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 1
  %"values_load" = load i64*, i64** %".7"
  %"old_values" = alloca i64*
  store i64* %"values_load", i64** %"old_values"
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".9" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 3
  %"cap_load" = load i64, i64* %".9"
  %"old_cap" = alloca i64
  store i64 %"cap_load", i64* %"old_cap"
  %"old_cap_load" = load i64, i64* %"old_cap"
  %"mul" = mul i64 %"old_cap_load", 2
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %"cap_ptr" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 3
  store i64 %"mul", i64* %"cap_ptr"
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"alloc_size" = mul i64 %"cap_load.1", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"self_load.5" = load %"Map"*, %"Map"** %"self"
  %"keys_ptr" = getelementptr %"Map", %"Map"* %"self_load.5", i32 0, i32 0
  %"keys_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"keys_bitcast", i64** %"keys_ptr"
  %"self_load.6" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.6", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".14"
  %"alloc_size.1" = mul i64 %"cap_load.2", 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"self_load.7" = load %"Map"*, %"Map"** %"self"
  %"values_ptr" = getelementptr %"Map", %"Map"* %"self_load.7", i32 0, i32 1
  %"values_bitcast" = bitcast i8* %"alloc_call.1" to i64*
  store i64* %"values_bitcast", i64** %"values_ptr"
  %"self_load.8" = load %"Map"*, %"Map"** %"self"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"self_load.8", i32 0, i32 2
  store i64 0, i64* %"size_ptr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"self_load.9" = load %"Map"*, %"Map"** %"self"
  %".19" = getelementptr %"Map", %"Map"* %"self_load.9", i32 0, i32 3
  %"cap_load.3" = load i64, i64* %".19"
  %"icmp" = icmp slt i64 %"i_load", %"cap_load.3"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"neg" = sub i64 0, 1
  %"self_load.10" = load %"Map"*, %"Map"** %"self"
  %".21" = getelementptr %"Map", %"Map"* %"self_load.10", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".21"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"i_load.1"
  store i64 %"neg", i64* %"idx_ptr"
  %"self_load.11" = load %"Map"*, %"Map"** %"self"
  %".23" = getelementptr %"Map", %"Map"* %"self_load.11", i32 0, i32 1
  %"values_load.1" = load i64*, i64** %".23"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr.1" = getelementptr i64, i64* %"values_load.1", i64 %"i_load.2"
  store i64 0, i64* %"idx_ptr.1"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"i.1" = alloca i64
  store i64 0, i64* %"i.1"
  br label %"while_cond.1"
while_cond.1:
  %"i_load.4" = load i64, i64* %"i.1"
  %"old_cap_load.1" = load i64, i64* %"old_cap"
  %"icmp.1" = icmp slt i64 %"i_load.4", %"old_cap_load.1"
  br i1 %"icmp.1", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"old_keys_load" = load i64*, i64** %"old_keys"
  %"i_load.5" = load i64, i64* %"i.1"
  %".30" = getelementptr i64, i64* %"old_keys_load", i64 %"i_load.5"
  %"ptr_idx_load" = load i64, i64* %".30"
  %"neg.1" = sub i64 0, 1
  %"icmp.2" = icmp ne i64 %"ptr_idx_load", %"neg.1"
  br i1 %"icmp.2", label %"and_rhs", label %"and_end"
while_end.1:
  ret void
and_rhs:
  %"old_keys_load.1" = load i64*, i64** %"old_keys"
  %"i_load.6" = load i64, i64* %"i.1"
  %".32" = getelementptr i64, i64* %"old_keys_load.1", i64 %"i_load.6"
  %"ptr_idx_load.1" = load i64, i64* %".32"
  %"neg.2" = sub i64 0, 2
  %"icmp.3" = icmp ne i64 %"ptr_idx_load.1", %"neg.2"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_body.1"], [%"icmp.3", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  %"self_load.12" = load %"Map"*, %"Map"** %"self"
  %"old_keys_load.2" = load i64*, i64** %"old_keys"
  %"i_load.7" = load i64, i64* %"i.1"
  %".35" = getelementptr i64, i64* %"old_keys_load.2", i64 %"i_load.7"
  %"ptr_idx_load.2" = load i64, i64* %".35"
  %"old_values_load" = load i64*, i64** %"old_values"
  %"i_load.8" = load i64, i64* %"i.1"
  %".36" = getelementptr i64, i64* %"old_values_load", i64 %"i_load.8"
  %"ptr_idx_load.3" = load i64, i64* %".36"
  call void @"Map_insert"(%"Map"* %"self_load.12", i64 %"ptr_idx_load.2", i64 %"ptr_idx_load.3")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.9" = load i64, i64* %"i.1"
  %"add.1" = add i64 %"i_load.9", 1
  store i64 %"add.1", i64* %"i.1"
  br label %"while_cond.1"
}

define void @"Map_insert"(%"Map"* %".1", i64 %".2", i64 %".3")
{
Map_insert_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  %"value" = alloca i64
  store i64 %".3", i64* %"value"
  br label %"Map_insert_body"
Map_insert_body:
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".9" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 2
  %"size_load" = load i64, i64* %".9"
  %"mul" = mul i64 %"size_load", 4
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".10" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load" = load i64, i64* %".10"
  %"mul.1" = mul i64 %"cap_load", 3
  %"icmp" = icmp sge i64 %"mul", %"mul.1"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  call void @"Map_rehash"(%"Map"* %"self_load.2")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"key_load" = load i64, i64* %"key"
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".14"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load.1")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  %"neg" = sub i64 0, 1
  %"first_tombstone" = alloca i64
  store i64 %"neg", i64* %"first_tombstone"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".20" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".20"
  %"icmp.1" = icmp slt i64 %"probes_load", %"cap_load.2"
  br i1 %"icmp.1", label %"while_body", label %"while_end"
while_body:
  %"self_load.5" = load %"Map"*, %"Map"** %"self"
  %".22" = getelementptr %"Map", %"Map"* %"self_load.5", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".22"
  %"i_load" = load i64, i64* %"i"
  %".23" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".23"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg.1" = sub i64 0, 1
  %"icmp.2" = icmp eq i64 %"k_load", %"neg.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
while_end:
  ret void
if_then.1:
  %"first_tombstone_load" = load i64, i64* %"first_tombstone"
  %"neg.2" = sub i64 0, 1
  %"icmp.3" = icmp ne i64 %"first_tombstone_load", %"neg.2"
  br i1 %"icmp.3", label %"if_then.2", label %"if_else.2"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"k_load.1" = load i64, i64* %"k"
  %"neg.3" = sub i64 0, 2
  %"icmp.4" = icmp eq i64 %"k_load.1", %"neg.3"
  br i1 %"icmp.4", label %"if_then.3", label %"if_else.3"
if_then.2:
  %"key_load.1" = load i64, i64* %"key"
  %"self_load.6" = load %"Map"*, %"Map"** %"self"
  %".27" = getelementptr %"Map", %"Map"* %"self_load.6", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".27"
  %"first_tombstone_load.1" = load i64, i64* %"first_tombstone"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"first_tombstone_load.1"
  store i64 %"key_load.1", i64* %"idx_ptr"
  %"value_load" = load i64, i64* %"value"
  %"self_load.7" = load %"Map"*, %"Map"** %"self"
  %".29" = getelementptr %"Map", %"Map"* %"self_load.7", i32 0, i32 1
  %"values_load" = load i64*, i64** %".29"
  %"first_tombstone_load.2" = load i64, i64* %"first_tombstone"
  %"idx_ptr.1" = getelementptr i64, i64* %"values_load", i64 %"first_tombstone_load.2"
  store i64 %"value_load", i64* %"idx_ptr.1"
  br label %"if_end.2"
if_else.2:
  %"key_load.2" = load i64, i64* %"key"
  %"self_load.8" = load %"Map"*, %"Map"** %"self"
  %".32" = getelementptr %"Map", %"Map"* %"self_load.8", i32 0, i32 0
  %"keys_load.2" = load i64*, i64** %".32"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr.2" = getelementptr i64, i64* %"keys_load.2", i64 %"i_load.1"
  store i64 %"key_load.2", i64* %"idx_ptr.2"
  %"value_load.1" = load i64, i64* %"value"
  %"self_load.9" = load %"Map"*, %"Map"** %"self"
  %".34" = getelementptr %"Map", %"Map"* %"self_load.9", i32 0, i32 1
  %"values_load.1" = load i64*, i64** %".34"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr.3" = getelementptr i64, i64* %"values_load.1", i64 %"i_load.2"
  store i64 %"value_load.1", i64* %"idx_ptr.3"
  br label %"if_end.2"
if_end.2:
  %"self_load.10" = load %"Map"*, %"Map"** %"self"
  %".37" = getelementptr %"Map", %"Map"* %"self_load.10", i32 0, i32 2
  %"size_load.1" = load i64, i64* %".37"
  %"add" = add i64 %"size_load.1", 1
  %"self_load.11" = load %"Map"*, %"Map"** %"self"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"self_load.11", i32 0, i32 2
  store i64 %"add", i64* %"size_ptr"
  ret void
if_then.3:
  %"first_tombstone_load.3" = load i64, i64* %"first_tombstone"
  %"neg.4" = sub i64 0, 1
  %"icmp.5" = icmp eq i64 %"first_tombstone_load.3", %"neg.4"
  br i1 %"icmp.5", label %"if_then.4", label %"if_else.4"
if_else.3:
  %"k_load.2" = load i64, i64* %"k"
  %"key_load.3" = load i64, i64* %"key"
  %"icmp.6" = icmp eq i64 %"k_load.2", %"key_load.3"
  br i1 %"icmp.6", label %"if_then.5", label %"if_else.5"
if_end.3:
  %"i_load.5" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.5", 1
  %"self_load.13" = load %"Map"*, %"Map"** %"self"
  %".53" = getelementptr %"Map", %"Map"* %"self_load.13", i32 0, i32 3
  %"cap_load.3" = load i64, i64* %".53"
  %"sub" = sub i64 %"cap_load.3", 1
  %"bitand" = and i64 %"add.1", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.2" = add i64 %"probes_load.1", 1
  store i64 %"add.2", i64* %"probes"
  br label %"while_cond"
if_then.4:
  %"i_load.3" = load i64, i64* %"i"
  store i64 %"i_load.3", i64* %"first_tombstone"
  br label %"if_end.4"
if_else.4:
  br label %"if_end.4"
if_end.4:
  br label %"if_end.3"
if_then.5:
  %"value_load.2" = load i64, i64* %"value"
  %"self_load.12" = load %"Map"*, %"Map"** %"self"
  %".48" = getelementptr %"Map", %"Map"* %"self_load.12", i32 0, i32 1
  %"values_load.2" = load i64*, i64** %".48"
  %"i_load.4" = load i64, i64* %"i"
  %"idx_ptr.4" = getelementptr i64, i64* %"values_load.2", i64 %"i_load.4"
  store i64 %"value_load.2", i64* %"idx_ptr.4"
  ret void
if_else.5:
  br label %"if_end.5"
if_end.5:
  br label %"if_end.3"
}

define i64 @"Map_get"(%"Map"* %".1", i64 %".2")
{
Map_get_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Map_get_body"
Map_get_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 3
  %"cap_load" = load i64, i64* %".7"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"neg.2" = sub i64 0, 1
  ret i64 %"neg.2"
if_then:
  %"neg.1" = sub i64 0, 1
  ret i64 %"neg.1"
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".21" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 1
  %"values_load" = load i64*, i64** %".21"
  %"i_load.1" = load i64, i64* %"i"
  %".22" = getelementptr i64, i64* %"values_load", i64 %"i_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".22"
  ret i64 %"ptr_idx_load.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".25" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".25"
  %"sub" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define i64 @"Map_contains"(%"Map"* %".1", i64 %".2")
{
Map_contains_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Map_contains_body"
Map_contains_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 3
  %"cap_load" = load i64, i64* %".7"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 0
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.1" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.1", 1
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".23" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".23"
  %"sub" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define i64 @"Map_remove"(%"Map"* %".1", i64 %".2")
{
Map_remove_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Map_remove_body"
Map_remove_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 3
  %"cap_load" = load i64, i64* %".7"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 0
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"neg.1" = sub i64 0, 2
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".21" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".21"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"i_load.1"
  store i64 %"neg.1", i64* %"idx_ptr"
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".23" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 2
  %"size_load" = load i64, i64* %".23"
  %"sub" = sub i64 %"size_load", 1
  %"self_load.5" = load %"Map"*, %"Map"** %"self"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"self_load.5", i32 0, i32 2
  store i64 %"sub", i64* %"size_ptr"
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %"self_load.6" = load %"Map"*, %"Map"** %"self"
  %".27" = getelementptr %"Map", %"Map"* %"self_load.6", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".27"
  %"sub.1" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub.1"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define %"Map"* @"new_map"()
{
new_map_entry:
  br label %"new_map_body"
new_map_body:
  %"m" = alloca %"Map"*
  %"m_storage_raw" = call i8* @"GC_malloc"(i64 32)
  %"m_storage" = bitcast i8* %"m_storage_raw" to %"Map"*
  store %"Map" {i64* null, i64* null, i64 0, i64 0}, %"Map"* %"m_storage"
  store %"Map"* %"m_storage", %"Map"** %"m"
  %"m_load" = load %"Map"*, %"Map"** %"m"
  %"cap_ptr" = getelementptr %"Map", %"Map"* %"m_load", i32 0, i32 3
  store i64 16, i64* %"cap_ptr"
  %"m_load.1" = load %"Map"*, %"Map"** %"m"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"m_load.1", i32 0, i32 2
  store i64 0, i64* %"size_ptr"
  %"alloc_size" = mul i64 16, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"m_load.2" = load %"Map"*, %"Map"** %"m"
  %"keys_ptr" = getelementptr %"Map", %"Map"* %"m_load.2", i32 0, i32 0
  %"keys_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"keys_bitcast", i64** %"keys_ptr"
  %"alloc_size.1" = mul i64 16, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"m_load.3" = load %"Map"*, %"Map"** %"m"
  %"values_ptr" = getelementptr %"Map", %"Map"* %"m_load.3", i32 0, i32 1
  %"values_bitcast" = bitcast i8* %"alloc_call.1" to i64*
  store i64* %"values_bitcast", i64** %"values_ptr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 16
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"neg" = sub i64 0, 1
  %"m_load.4" = load %"Map"*, %"Map"** %"m"
  %".12" = getelementptr %"Map", %"Map"* %"m_load.4", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".12"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load", i64 %"i_load.1"
  store i64 %"neg", i64* %"idx_ptr"
  %"m_load.5" = load %"Map"*, %"Map"** %"m"
  %".14" = getelementptr %"Map", %"Map"* %"m_load.5", i32 0, i32 1
  %"values_load" = load i64*, i64** %".14"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr.1" = getelementptr i64, i64* %"values_load", i64 %"i_load.2"
  store i64 0, i64* %"idx_ptr.1"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"m_load.6" = load %"Map"*, %"Map"** %"m"
  ret %"Map"* %"m_load.6"
}

define i64 @"_set_hash"(i64 %".1", i64 %".2")
{
_set_hash_entry:
  %"key" = alloca i64
  store i64 %".1", i64* %"key"
  %"cap" = alloca i64
  store i64 %".2", i64* %"cap"
  br label %"_set_hash_body"
_set_hash_body:
  %"key_load" = load i64, i64* %"key"
  %"cap_load" = load i64, i64* %"cap"
  %"sub" = sub i64 %"cap_load", 1
  %"bitand" = and i64 %"key_load", %"sub"
  ret i64 %"bitand"
}

define void @"Set_rehash"(%"Set"* %".1")
{
Set_rehash_entry:
  %"self" = alloca %"Set"*
  store %"Set"* %".1", %"Set"** %"self"
  br label %"Set_rehash_body"
Set_rehash_body:
  %"self_load" = load %"Set"*, %"Set"** %"self"
  %".5" = getelementptr %"Set", %"Set"* %"self_load", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".5"
  %"old_keys" = alloca i64*
  store i64* %"keys_load", i64** %"old_keys"
  %"self_load.1" = load %"Set"*, %"Set"** %"self"
  %".7" = getelementptr %"Set", %"Set"* %"self_load.1", i32 0, i32 2
  %"cap_load" = load i64, i64* %".7"
  %"old_cap" = alloca i64
  store i64 %"cap_load", i64* %"old_cap"
  %"old_cap_load" = load i64, i64* %"old_cap"
  %"mul" = mul i64 %"old_cap_load", 2
  %"self_load.2" = load %"Set"*, %"Set"** %"self"
  %"cap_ptr" = getelementptr %"Set", %"Set"* %"self_load.2", i32 0, i32 2
  store i64 %"mul", i64* %"cap_ptr"
  %"self_load.3" = load %"Set"*, %"Set"** %"self"
  %".10" = getelementptr %"Set", %"Set"* %"self_load.3", i32 0, i32 2
  %"cap_load.1" = load i64, i64* %".10"
  %"alloc_size" = mul i64 %"cap_load.1", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"self_load.4" = load %"Set"*, %"Set"** %"self"
  %"keys_ptr" = getelementptr %"Set", %"Set"* %"self_load.4", i32 0, i32 0
  %"keys_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"keys_bitcast", i64** %"keys_ptr"
  %"self_load.5" = load %"Set"*, %"Set"** %"self"
  %"size_ptr" = getelementptr %"Set", %"Set"* %"self_load.5", i32 0, i32 1
  store i64 0, i64* %"size_ptr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"self_load.6" = load %"Set"*, %"Set"** %"self"
  %".15" = getelementptr %"Set", %"Set"* %"self_load.6", i32 0, i32 2
  %"cap_load.2" = load i64, i64* %".15"
  %"icmp" = icmp slt i64 %"i_load", %"cap_load.2"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"neg" = sub i64 0, 1
  %"self_load.7" = load %"Set"*, %"Set"** %"self"
  %".17" = getelementptr %"Set", %"Set"* %"self_load.7", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".17"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"i_load.1"
  store i64 %"neg", i64* %"idx_ptr"
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"i.1" = alloca i64
  store i64 0, i64* %"i.1"
  br label %"while_cond.1"
while_cond.1:
  %"i_load.3" = load i64, i64* %"i.1"
  %"old_cap_load.1" = load i64, i64* %"old_cap"
  %"icmp.1" = icmp slt i64 %"i_load.3", %"old_cap_load.1"
  br i1 %"icmp.1", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"old_keys_load" = load i64*, i64** %"old_keys"
  %"i_load.4" = load i64, i64* %"i.1"
  %".24" = getelementptr i64, i64* %"old_keys_load", i64 %"i_load.4"
  %"ptr_idx_load" = load i64, i64* %".24"
  %"neg.1" = sub i64 0, 1
  %"icmp.2" = icmp ne i64 %"ptr_idx_load", %"neg.1"
  br i1 %"icmp.2", label %"and_rhs", label %"and_end"
while_end.1:
  ret void
and_rhs:
  %"old_keys_load.1" = load i64*, i64** %"old_keys"
  %"i_load.5" = load i64, i64* %"i.1"
  %".26" = getelementptr i64, i64* %"old_keys_load.1", i64 %"i_load.5"
  %"ptr_idx_load.1" = load i64, i64* %".26"
  %"neg.2" = sub i64 0, 2
  %"icmp.3" = icmp ne i64 %"ptr_idx_load.1", %"neg.2"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_body.1"], [%"icmp.3", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  %"self_load.8" = load %"Set"*, %"Set"** %"self"
  %"old_keys_load.2" = load i64*, i64** %"old_keys"
  %"i_load.6" = load i64, i64* %"i.1"
  %".29" = getelementptr i64, i64* %"old_keys_load.2", i64 %"i_load.6"
  %"ptr_idx_load.2" = load i64, i64* %".29"
  call void @"Set_add"(%"Set"* %"self_load.8", i64 %"ptr_idx_load.2")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.7" = load i64, i64* %"i.1"
  %"add.1" = add i64 %"i_load.7", 1
  store i64 %"add.1", i64* %"i.1"
  br label %"while_cond.1"
}

define void @"Set_add"(%"Set"* %".1", i64 %".2")
{
Set_add_entry:
  %"self" = alloca %"Set"*
  store %"Set"* %".1", %"Set"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Set_add_body"
Set_add_body:
  %"self_load" = load %"Set"*, %"Set"** %"self"
  %".7" = getelementptr %"Set", %"Set"* %"self_load", i32 0, i32 1
  %"size_load" = load i64, i64* %".7"
  %"mul" = mul i64 %"size_load", 4
  %"self_load.1" = load %"Set"*, %"Set"** %"self"
  %".8" = getelementptr %"Set", %"Set"* %"self_load.1", i32 0, i32 2
  %"cap_load" = load i64, i64* %".8"
  %"mul.1" = mul i64 %"cap_load", 3
  %"icmp" = icmp sge i64 %"mul", %"mul.1"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"Set"*, %"Set"** %"self"
  call void @"Set_rehash"(%"Set"* %"self_load.2")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"key_load" = load i64, i64* %"key"
  %"self_load.3" = load %"Set"*, %"Set"** %"self"
  %".12" = getelementptr %"Set", %"Set"* %"self_load.3", i32 0, i32 2
  %"cap_load.1" = load i64, i64* %".12"
  %"_set_hash_call" = call i64 @"_set_hash"(i64 %"key_load", i64 %"cap_load.1")
  %"idx" = alloca i64
  store i64 %"_set_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  %"neg" = sub i64 0, 1
  %"first_tombstone" = alloca i64
  store i64 %"neg", i64* %"first_tombstone"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.4" = load %"Set"*, %"Set"** %"self"
  %".18" = getelementptr %"Set", %"Set"* %"self_load.4", i32 0, i32 2
  %"cap_load.2" = load i64, i64* %".18"
  %"icmp.1" = icmp slt i64 %"probes_load", %"cap_load.2"
  br i1 %"icmp.1", label %"while_body", label %"while_end"
while_body:
  %"self_load.5" = load %"Set"*, %"Set"** %"self"
  %".20" = getelementptr %"Set", %"Set"* %"self_load.5", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".20"
  %"i_load" = load i64, i64* %"i"
  %".21" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".21"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg.1" = sub i64 0, 1
  %"icmp.2" = icmp eq i64 %"k_load", %"neg.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
while_end:
  ret void
if_then.1:
  %"first_tombstone_load" = load i64, i64* %"first_tombstone"
  %"neg.2" = sub i64 0, 1
  %"icmp.3" = icmp ne i64 %"first_tombstone_load", %"neg.2"
  br i1 %"icmp.3", label %"if_then.2", label %"if_else.2"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"k_load.1" = load i64, i64* %"k"
  %"neg.3" = sub i64 0, 2
  %"icmp.4" = icmp eq i64 %"k_load.1", %"neg.3"
  br i1 %"icmp.4", label %"if_then.3", label %"if_else.3"
if_then.2:
  %"key_load.1" = load i64, i64* %"key"
  %"self_load.6" = load %"Set"*, %"Set"** %"self"
  %".25" = getelementptr %"Set", %"Set"* %"self_load.6", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".25"
  %"first_tombstone_load.1" = load i64, i64* %"first_tombstone"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"first_tombstone_load.1"
  store i64 %"key_load.1", i64* %"idx_ptr"
  br label %"if_end.2"
if_else.2:
  %"key_load.2" = load i64, i64* %"key"
  %"self_load.7" = load %"Set"*, %"Set"** %"self"
  %".28" = getelementptr %"Set", %"Set"* %"self_load.7", i32 0, i32 0
  %"keys_load.2" = load i64*, i64** %".28"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr.1" = getelementptr i64, i64* %"keys_load.2", i64 %"i_load.1"
  store i64 %"key_load.2", i64* %"idx_ptr.1"
  br label %"if_end.2"
if_end.2:
  %"self_load.8" = load %"Set"*, %"Set"** %"self"
  %".31" = getelementptr %"Set", %"Set"* %"self_load.8", i32 0, i32 1
  %"size_load.1" = load i64, i64* %".31"
  %"add" = add i64 %"size_load.1", 1
  %"self_load.9" = load %"Set"*, %"Set"** %"self"
  %"size_ptr" = getelementptr %"Set", %"Set"* %"self_load.9", i32 0, i32 1
  store i64 %"add", i64* %"size_ptr"
  ret void
if_then.3:
  %"first_tombstone_load.2" = load i64, i64* %"first_tombstone"
  %"neg.4" = sub i64 0, 1
  %"icmp.5" = icmp eq i64 %"first_tombstone_load.2", %"neg.4"
  br i1 %"icmp.5", label %"if_then.4", label %"if_else.4"
if_else.3:
  %"k_load.2" = load i64, i64* %"k"
  %"key_load.3" = load i64, i64* %"key"
  %"icmp.6" = icmp eq i64 %"k_load.2", %"key_load.3"
  br i1 %"icmp.6", label %"if_then.5", label %"if_else.5"
if_end.3:
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 1
  %"self_load.10" = load %"Set"*, %"Set"** %"self"
  %".45" = getelementptr %"Set", %"Set"* %"self_load.10", i32 0, i32 2
  %"cap_load.3" = load i64, i64* %".45"
  %"sub" = sub i64 %"cap_load.3", 1
  %"bitand" = and i64 %"add.1", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.2" = add i64 %"probes_load.1", 1
  store i64 %"add.2", i64* %"probes"
  br label %"while_cond"
if_then.4:
  %"i_load.2" = load i64, i64* %"i"
  store i64 %"i_load.2", i64* %"first_tombstone"
  br label %"if_end.4"
if_else.4:
  br label %"if_end.4"
if_end.4:
  br label %"if_end.3"
if_then.5:
  ret void
if_else.5:
  br label %"if_end.5"
if_end.5:
  br label %"if_end.3"
}

define i64 @"Set_contains"(%"Set"* %".1", i64 %".2")
{
Set_contains_entry:
  %"self" = alloca %"Set"*
  store %"Set"* %".1", %"Set"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Set_contains_body"
Set_contains_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Set"*, %"Set"** %"self"
  %".7" = getelementptr %"Set", %"Set"* %"self_load", i32 0, i32 2
  %"cap_load" = load i64, i64* %".7"
  %"_set_hash_call" = call i64 @"_set_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_set_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Set"*, %"Set"** %"self"
  %".12" = getelementptr %"Set", %"Set"* %"self_load.1", i32 0, i32 2
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Set"*, %"Set"** %"self"
  %".14" = getelementptr %"Set", %"Set"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 0
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.1" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.1", 1
  %"self_load.3" = load %"Set"*, %"Set"** %"self"
  %".23" = getelementptr %"Set", %"Set"* %"self_load.3", i32 0, i32 2
  %"cap_load.2" = load i64, i64* %".23"
  %"sub" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define i64 @"Set_remove"(%"Set"* %".1", i64 %".2")
{
Set_remove_entry:
  %"self" = alloca %"Set"*
  store %"Set"* %".1", %"Set"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Set_remove_body"
Set_remove_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Set"*, %"Set"** %"self"
  %".7" = getelementptr %"Set", %"Set"* %"self_load", i32 0, i32 2
  %"cap_load" = load i64, i64* %".7"
  %"_set_hash_call" = call i64 @"_set_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_set_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Set"*, %"Set"** %"self"
  %".12" = getelementptr %"Set", %"Set"* %"self_load.1", i32 0, i32 2
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Set"*, %"Set"** %"self"
  %".14" = getelementptr %"Set", %"Set"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 0
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"neg.1" = sub i64 0, 2
  %"self_load.3" = load %"Set"*, %"Set"** %"self"
  %".21" = getelementptr %"Set", %"Set"* %"self_load.3", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".21"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"i_load.1"
  store i64 %"neg.1", i64* %"idx_ptr"
  %"self_load.4" = load %"Set"*, %"Set"** %"self"
  %".23" = getelementptr %"Set", %"Set"* %"self_load.4", i32 0, i32 1
  %"size_load" = load i64, i64* %".23"
  %"sub" = sub i64 %"size_load", 1
  %"self_load.5" = load %"Set"*, %"Set"** %"self"
  %"size_ptr" = getelementptr %"Set", %"Set"* %"self_load.5", i32 0, i32 1
  store i64 %"sub", i64* %"size_ptr"
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %"self_load.6" = load %"Set"*, %"Set"** %"self"
  %".27" = getelementptr %"Set", %"Set"* %"self_load.6", i32 0, i32 2
  %"cap_load.2" = load i64, i64* %".27"
  %"sub.1" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub.1"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define %"Set"* @"new_set"()
{
new_set_entry:
  br label %"new_set_body"
new_set_body:
  %"s" = alloca %"Set"*
  %"s_storage_raw" = call i8* @"GC_malloc"(i64 24)
  %"s_storage" = bitcast i8* %"s_storage_raw" to %"Set"*
  store %"Set" {i64* null, i64 0, i64 0}, %"Set"* %"s_storage"
  store %"Set"* %"s_storage", %"Set"** %"s"
  %"s_load" = load %"Set"*, %"Set"** %"s"
  %"cap_ptr" = getelementptr %"Set", %"Set"* %"s_load", i32 0, i32 2
  store i64 16, i64* %"cap_ptr"
  %"s_load.1" = load %"Set"*, %"Set"** %"s"
  %"size_ptr" = getelementptr %"Set", %"Set"* %"s_load.1", i32 0, i32 1
  store i64 0, i64* %"size_ptr"
  %"alloc_size" = mul i64 16, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"s_load.2" = load %"Set"*, %"Set"** %"s"
  %"keys_ptr" = getelementptr %"Set", %"Set"* %"s_load.2", i32 0, i32 0
  %"keys_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"keys_bitcast", i64** %"keys_ptr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 16
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"neg" = sub i64 0, 1
  %"s_load.3" = load %"Set"*, %"Set"** %"s"
  %".11" = getelementptr %"Set", %"Set"* %"s_load.3", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".11"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load", i64 %"i_load.1"
  store i64 %"neg", i64* %"idx_ptr"
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"s_load.4" = load %"Set"*, %"Set"** %"s"
  ret %"Set"* %"s_load.4"
}

define i64 @"Deque__phys"(%"Deque"* %".1", i64 %".2")
{
Deque__phys_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  %"i" = alloca i64
  store i64 %".2", i64* %"i"
  br label %"Deque__phys_body"
Deque__phys_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %".7" = getelementptr %"Deque", %"Deque"* %"self_load", i32 0, i32 1
  %"head_load" = load i64, i64* %".7"
  %"i_load" = load i64, i64* %"i"
  %"add" = add i64 %"head_load", %"i_load"
  %"self_load.1" = load %"Deque"*, %"Deque"** %"self"
  %".8" = getelementptr %"Deque", %"Deque"* %"self_load.1", i32 0, i32 3
  %"cap_load" = load i64, i64* %".8"
  %"sub" = sub i64 %"cap_load", 1
  %"bitand" = and i64 %"add", %"sub"
  ret i64 %"bitand"
}

define void @"Deque_grow"(%"Deque"* %".1")
{
Deque_grow_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  br label %"Deque_grow_body"
Deque_grow_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %".5" = getelementptr %"Deque", %"Deque"* %"self_load", i32 0, i32 3
  %"cap_load" = load i64, i64* %".5"
  %"old_cap" = alloca i64
  store i64 %"cap_load", i64* %"old_cap"
  %"old_cap_load" = load i64, i64* %"old_cap"
  %"mul" = mul i64 %"old_cap_load", 2
  %"self_load.1" = load %"Deque"*, %"Deque"** %"self"
  %"cap_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.1", i32 0, i32 3
  store i64 %"mul", i64* %"cap_ptr"
  %"self_load.2" = load %"Deque"*, %"Deque"** %"self"
  %".8" = getelementptr %"Deque", %"Deque"* %"self_load.2", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".8"
  %"alloc_size" = mul i64 %"cap_load.1", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"new_data" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"new_data"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"self_load.3" = load %"Deque"*, %"Deque"** %"self"
  %".12" = getelementptr %"Deque", %"Deque"* %"self_load.3", i32 0, i32 2
  %"size_load" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"i_load", %"size_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.4" = load %"Deque"*, %"Deque"** %"self"
  %".14" = getelementptr %"Deque", %"Deque"* %"self_load.4", i32 0, i32 1
  %"head_load" = load i64, i64* %".14"
  %"i_load.1" = load i64, i64* %"i"
  %"add" = add i64 %"head_load", %"i_load.1"
  %"old_cap_load.1" = load i64, i64* %"old_cap"
  %"sub" = sub i64 %"old_cap_load.1", 1
  %"bitand" = and i64 %"add", %"sub"
  %"old_phys" = alloca i64
  store i64 %"bitand", i64* %"old_phys"
  %"self_load.5" = load %"Deque"*, %"Deque"** %"self"
  %".16" = getelementptr %"Deque", %"Deque"* %"self_load.5", i32 0, i32 0
  %"data_load" = load i64*, i64** %".16"
  %"old_phys_load" = load i64, i64* %"old_phys"
  %".17" = getelementptr i64, i64* %"data_load", i64 %"old_phys_load"
  %"ptr_idx_load" = load i64, i64* %".17"
  %"new_data_load" = load i64*, i64** %"new_data"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"new_data_load", i64 %"i_load.2"
  store i64 %"ptr_idx_load", i64* %"idx_ptr"
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %"new_data_load.1" = load i64*, i64** %"new_data"
  %"self_load.6" = load %"Deque"*, %"Deque"** %"self"
  %"data_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.6", i32 0, i32 0
  store i64* %"new_data_load.1", i64** %"data_ptr"
  %"self_load.7" = load %"Deque"*, %"Deque"** %"self"
  %"head_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.7", i32 0, i32 1
  store i64 0, i64* %"head_ptr"
  ret void
}

define void @"Deque_push_back"(%"Deque"* %".1", i64 %".2")
{
Deque_push_back_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  %"value" = alloca i64
  store i64 %".2", i64* %"value"
  br label %"Deque_push_back_body"
Deque_push_back_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %".7" = getelementptr %"Deque", %"Deque"* %"self_load", i32 0, i32 2
  %"size_load" = load i64, i64* %".7"
  %"self_load.1" = load %"Deque"*, %"Deque"** %"self"
  %".8" = getelementptr %"Deque", %"Deque"* %"self_load.1", i32 0, i32 3
  %"cap_load" = load i64, i64* %".8"
  %"icmp" = icmp sge i64 %"size_load", %"cap_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"Deque"*, %"Deque"** %"self"
  call void @"Deque_grow"(%"Deque"* %"self_load.2")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"self_load.3" = load %"Deque"*, %"Deque"** %"self"
  %"self_load.4" = load %"Deque"*, %"Deque"** %"self"
  %".12" = getelementptr %"Deque", %"Deque"* %"self_load.4", i32 0, i32 2
  %"size_load.1" = load i64, i64* %".12"
  %"Deque__phys_call" = call i64 @"Deque__phys"(%"Deque"* %"self_load.3", i64 %"size_load.1")
  %"idx" = alloca i64
  store i64 %"Deque__phys_call", i64* %"idx"
  %"value_load" = load i64, i64* %"value"
  %"self_load.5" = load %"Deque"*, %"Deque"** %"self"
  %".14" = getelementptr %"Deque", %"Deque"* %"self_load.5", i32 0, i32 0
  %"data_load" = load i64*, i64** %".14"
  %"idx_load" = load i64, i64* %"idx"
  %"idx_ptr" = getelementptr i64, i64* %"data_load", i64 %"idx_load"
  store i64 %"value_load", i64* %"idx_ptr"
  %"self_load.6" = load %"Deque"*, %"Deque"** %"self"
  %".16" = getelementptr %"Deque", %"Deque"* %"self_load.6", i32 0, i32 2
  %"size_load.2" = load i64, i64* %".16"
  %"add" = add i64 %"size_load.2", 1
  %"self_load.7" = load %"Deque"*, %"Deque"** %"self"
  %"size_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.7", i32 0, i32 2
  store i64 %"add", i64* %"size_ptr"
  ret void
}

define void @"Deque_push_front"(%"Deque"* %".1", i64 %".2")
{
Deque_push_front_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  %"value" = alloca i64
  store i64 %".2", i64* %"value"
  br label %"Deque_push_front_body"
Deque_push_front_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %".7" = getelementptr %"Deque", %"Deque"* %"self_load", i32 0, i32 2
  %"size_load" = load i64, i64* %".7"
  %"self_load.1" = load %"Deque"*, %"Deque"** %"self"
  %".8" = getelementptr %"Deque", %"Deque"* %"self_load.1", i32 0, i32 3
  %"cap_load" = load i64, i64* %".8"
  %"icmp" = icmp sge i64 %"size_load", %"cap_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"Deque"*, %"Deque"** %"self"
  call void @"Deque_grow"(%"Deque"* %"self_load.2")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"self_load.3" = load %"Deque"*, %"Deque"** %"self"
  %".12" = getelementptr %"Deque", %"Deque"* %"self_load.3", i32 0, i32 1
  %"head_load" = load i64, i64* %".12"
  %"sub" = sub i64 %"head_load", 1
  %"self_load.4" = load %"Deque"*, %"Deque"** %"self"
  %".13" = getelementptr %"Deque", %"Deque"* %"self_load.4", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".13"
  %"sub.1" = sub i64 %"cap_load.1", 1
  %"bitand" = and i64 %"sub", %"sub.1"
  %"self_load.5" = load %"Deque"*, %"Deque"** %"self"
  %"head_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.5", i32 0, i32 1
  store i64 %"bitand", i64* %"head_ptr"
  %"value_load" = load i64, i64* %"value"
  %"self_load.6" = load %"Deque"*, %"Deque"** %"self"
  %".15" = getelementptr %"Deque", %"Deque"* %"self_load.6", i32 0, i32 0
  %"data_load" = load i64*, i64** %".15"
  %"self_load.7" = load %"Deque"*, %"Deque"** %"self"
  %".16" = getelementptr %"Deque", %"Deque"* %"self_load.7", i32 0, i32 1
  %"head_load.1" = load i64, i64* %".16"
  %"idx_ptr" = getelementptr i64, i64* %"data_load", i64 %"head_load.1"
  store i64 %"value_load", i64* %"idx_ptr"
  %"self_load.8" = load %"Deque"*, %"Deque"** %"self"
  %".18" = getelementptr %"Deque", %"Deque"* %"self_load.8", i32 0, i32 2
  %"size_load.1" = load i64, i64* %".18"
  %"add" = add i64 %"size_load.1", 1
  %"self_load.9" = load %"Deque"*, %"Deque"** %"self"
  %"size_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.9", i32 0, i32 2
  store i64 %"add", i64* %"size_ptr"
  ret void
}

define i64 @"Deque_pop_front"(%"Deque"* %".1")
{
Deque_pop_front_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  br label %"Deque_pop_front_body"
Deque_pop_front_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %".5" = getelementptr %"Deque", %"Deque"* %"self_load", i32 0, i32 0
  %"data_load" = load i64*, i64** %".5"
  %"self_load.1" = load %"Deque"*, %"Deque"** %"self"
  %".6" = getelementptr %"Deque", %"Deque"* %"self_load.1", i32 0, i32 1
  %"head_load" = load i64, i64* %".6"
  %".7" = getelementptr i64, i64* %"data_load", i64 %"head_load"
  %"ptr_idx_load" = load i64, i64* %".7"
  %"val" = alloca i64
  store i64 %"ptr_idx_load", i64* %"val"
  %"self_load.2" = load %"Deque"*, %"Deque"** %"self"
  %".9" = getelementptr %"Deque", %"Deque"* %"self_load.2", i32 0, i32 1
  %"head_load.1" = load i64, i64* %".9"
  %"add" = add i64 %"head_load.1", 1
  %"self_load.3" = load %"Deque"*, %"Deque"** %"self"
  %".10" = getelementptr %"Deque", %"Deque"* %"self_load.3", i32 0, i32 3
  %"cap_load" = load i64, i64* %".10"
  %"sub" = sub i64 %"cap_load", 1
  %"bitand" = and i64 %"add", %"sub"
  %"self_load.4" = load %"Deque"*, %"Deque"** %"self"
  %"head_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.4", i32 0, i32 1
  store i64 %"bitand", i64* %"head_ptr"
  %"self_load.5" = load %"Deque"*, %"Deque"** %"self"
  %".12" = getelementptr %"Deque", %"Deque"* %"self_load.5", i32 0, i32 2
  %"size_load" = load i64, i64* %".12"
  %"sub.1" = sub i64 %"size_load", 1
  %"self_load.6" = load %"Deque"*, %"Deque"** %"self"
  %"size_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.6", i32 0, i32 2
  store i64 %"sub.1", i64* %"size_ptr"
  %"val_load" = load i64, i64* %"val"
  ret i64 %"val_load"
}

define i64 @"Deque_pop_back"(%"Deque"* %".1")
{
Deque_pop_back_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  br label %"Deque_pop_back_body"
Deque_pop_back_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %"self_load.1" = load %"Deque"*, %"Deque"** %"self"
  %".5" = getelementptr %"Deque", %"Deque"* %"self_load.1", i32 0, i32 2
  %"size_load" = load i64, i64* %".5"
  %"sub" = sub i64 %"size_load", 1
  %"Deque__phys_call" = call i64 @"Deque__phys"(%"Deque"* %"self_load", i64 %"sub")
  %"idx" = alloca i64
  store i64 %"Deque__phys_call", i64* %"idx"
  %"self_load.2" = load %"Deque"*, %"Deque"** %"self"
  %".7" = getelementptr %"Deque", %"Deque"* %"self_load.2", i32 0, i32 0
  %"data_load" = load i64*, i64** %".7"
  %"idx_load" = load i64, i64* %"idx"
  %".8" = getelementptr i64, i64* %"data_load", i64 %"idx_load"
  %"ptr_idx_load" = load i64, i64* %".8"
  %"val" = alloca i64
  store i64 %"ptr_idx_load", i64* %"val"
  %"self_load.3" = load %"Deque"*, %"Deque"** %"self"
  %".10" = getelementptr %"Deque", %"Deque"* %"self_load.3", i32 0, i32 2
  %"size_load.1" = load i64, i64* %".10"
  %"sub.1" = sub i64 %"size_load.1", 1
  %"self_load.4" = load %"Deque"*, %"Deque"** %"self"
  %"size_ptr" = getelementptr %"Deque", %"Deque"* %"self_load.4", i32 0, i32 2
  store i64 %"sub.1", i64* %"size_ptr"
  %"val_load" = load i64, i64* %"val"
  ret i64 %"val_load"
}

define i64 @"Deque_get"(%"Deque"* %".1", i64 %".2")
{
Deque_get_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  %"i" = alloca i64
  store i64 %".2", i64* %"i"
  br label %"Deque_get_body"
Deque_get_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %".7" = getelementptr %"Deque", %"Deque"* %"self_load", i32 0, i32 0
  %"data_load" = load i64*, i64** %".7"
  %"self_load.1" = load %"Deque"*, %"Deque"** %"self"
  %"i_load" = load i64, i64* %"i"
  %"Deque__phys_call" = call i64 @"Deque__phys"(%"Deque"* %"self_load.1", i64 %"i_load")
  %".8" = getelementptr i64, i64* %"data_load", i64 %"Deque__phys_call"
  %"ptr_idx_load" = load i64, i64* %".8"
  ret i64 %"ptr_idx_load"
}

define i64 @"Deque_is_empty"(%"Deque"* %".1")
{
Deque_is_empty_entry:
  %"self" = alloca %"Deque"*
  store %"Deque"* %".1", %"Deque"** %"self"
  br label %"Deque_is_empty_body"
Deque_is_empty_body:
  %"self_load" = load %"Deque"*, %"Deque"** %"self"
  %".5" = getelementptr %"Deque", %"Deque"* %"self_load", i32 0, i32 2
  %"size_load" = load i64, i64* %".5"
  %"icmp" = icmp eq i64 %"size_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret i64 1
if_else:
  br label %"if_end"
if_end:
  ret i64 0
}

define %"Deque"* @"new_deque"()
{
new_deque_entry:
  br label %"new_deque_body"
new_deque_body:
  %"d" = alloca %"Deque"*
  %"d_storage_raw" = call i8* @"GC_malloc"(i64 32)
  %"d_storage" = bitcast i8* %"d_storage_raw" to %"Deque"*
  store %"Deque" {i64* null, i64 0, i64 0, i64 0}, %"Deque"* %"d_storage"
  store %"Deque"* %"d_storage", %"Deque"** %"d"
  %"d_load" = load %"Deque"*, %"Deque"** %"d"
  %"cap_ptr" = getelementptr %"Deque", %"Deque"* %"d_load", i32 0, i32 3
  store i64 16, i64* %"cap_ptr"
  %"d_load.1" = load %"Deque"*, %"Deque"** %"d"
  %"head_ptr" = getelementptr %"Deque", %"Deque"* %"d_load.1", i32 0, i32 1
  store i64 0, i64* %"head_ptr"
  %"d_load.2" = load %"Deque"*, %"Deque"** %"d"
  %"size_ptr" = getelementptr %"Deque", %"Deque"* %"d_load.2", i32 0, i32 2
  store i64 0, i64* %"size_ptr"
  %"alloc_size" = mul i64 16, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"d_load.3" = load %"Deque"*, %"Deque"** %"d"
  %"data_ptr" = getelementptr %"Deque", %"Deque"* %"d_load.3", i32 0, i32 0
  %"data_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"data_bitcast", i64** %"data_ptr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 16
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"d_load.4" = load %"Deque"*, %"Deque"** %"d"
  %".12" = getelementptr %"Deque", %"Deque"* %"d_load.4", i32 0, i32 0
  %"data_load" = load i64*, i64** %".12"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"data_load", i64 %"i_load.1"
  store i64 0, i64* %"idx_ptr"
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"d_load.5" = load %"Deque"*, %"Deque"** %"d"
  ret %"Deque"* %"d_load.5"
}

@"str_0" = constant [23 x i8] c"=== Map com rehash ===\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [6 x i8] c"size:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [8 x i8] c"get(0):\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [9 x i8] c"get(50):\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [9 x i8] c"get(99):\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"
@"str_23" = constant [10 x i8] c"get(100):\00"
@"str_24" = constant [3 x i8] c"%s\00"
@"str_25" = constant [2 x i8] c" \00"
@"str_26" = constant [4 x i8] c"%ld\00"
@"str_27" = constant [2 x i8] c"\0a\00"
@"str_28" = constant [14 x i8] c"contains(42):\00"
@"str_29" = constant [3 x i8] c"%s\00"
@"str_30" = constant [2 x i8] c" \00"
@"str_31" = constant [4 x i8] c"%ld\00"
@"str_32" = constant [2 x i8] c"\0a\00"
@"str_33" = constant [15 x i8] c"contains(100):\00"
@"str_34" = constant [3 x i8] c"%s\00"
@"str_35" = constant [2 x i8] c" \00"
@"str_36" = constant [4 x i8] c"%ld\00"
@"str_37" = constant [2 x i8] c"\0a\00"
@"str_38" = constant [34 x i8] c"=== Map com remove + reinsert ===\00"
@"str_39" = constant [3 x i8] c"%s\00"
@"str_40" = constant [2 x i8] c"\0a\00"
@"str_41" = constant [14 x i8] c"contains(50):\00"
@"str_42" = constant [3 x i8] c"%s\00"
@"str_43" = constant [2 x i8] c" \00"
@"str_44" = constant [4 x i8] c"%ld\00"
@"str_45" = constant [2 x i8] c"\0a\00"
@"str_46" = constant [9 x i8] c"get(50):\00"
@"str_47" = constant [3 x i8] c"%s\00"
@"str_48" = constant [2 x i8] c" \00"
@"str_49" = constant [4 x i8] c"%ld\00"
@"str_50" = constant [2 x i8] c"\0a\00"
@"str_51" = constant [9 x i8] c"get(50):\00"
@"str_52" = constant [3 x i8] c"%s\00"
@"str_53" = constant [2 x i8] c" \00"
@"str_54" = constant [4 x i8] c"%ld\00"
@"str_55" = constant [2 x i8] c"\0a\00"
@"str_56" = constant [23 x i8] c"=== Set com rehash ===\00"
@"str_57" = constant [3 x i8] c"%s\00"
@"str_58" = constant [2 x i8] c"\0a\00"
@"str_59" = constant [6 x i8] c"size:\00"
@"str_60" = constant [3 x i8] c"%s\00"
@"str_61" = constant [2 x i8] c" \00"
@"str_62" = constant [4 x i8] c"%ld\00"
@"str_63" = constant [2 x i8] c"\0a\00"
@"str_64" = constant [13 x i8] c"contains(0):\00"
@"str_65" = constant [3 x i8] c"%s\00"
@"str_66" = constant [2 x i8] c" \00"
@"str_67" = constant [4 x i8] c"%ld\00"
@"str_68" = constant [2 x i8] c"\0a\00"
@"str_69" = constant [14 x i8] c"contains(99):\00"
@"str_70" = constant [3 x i8] c"%s\00"
@"str_71" = constant [2 x i8] c" \00"
@"str_72" = constant [4 x i8] c"%ld\00"
@"str_73" = constant [2 x i8] c"\0a\00"
@"str_74" = constant [15 x i8] c"contains(100):\00"
@"str_75" = constant [3 x i8] c"%s\00"
@"str_76" = constant [2 x i8] c" \00"
@"str_77" = constant [4 x i8] c"%ld\00"
@"str_78" = constant [2 x i8] c"\0a\00"
@"str_79" = constant [23 x i8] c"=== Deque com grow ===\00"
@"str_80" = constant [3 x i8] c"%s\00"
@"str_81" = constant [2 x i8] c"\0a\00"
@"str_82" = constant [6 x i8] c"size:\00"
@"str_83" = constant [3 x i8] c"%s\00"
@"str_84" = constant [2 x i8] c" \00"
@"str_85" = constant [4 x i8] c"%ld\00"
@"str_86" = constant [2 x i8] c"\0a\00"
@"str_87" = constant [8 x i8] c"get(0):\00"
@"str_88" = constant [3 x i8] c"%s\00"
@"str_89" = constant [2 x i8] c" \00"
@"str_90" = constant [4 x i8] c"%ld\00"
@"str_91" = constant [2 x i8] c"\0a\00"
@"str_92" = constant [9 x i8] c"get(50):\00"
@"str_93" = constant [3 x i8] c"%s\00"
@"str_94" = constant [2 x i8] c" \00"
@"str_95" = constant [4 x i8] c"%ld\00"
@"str_96" = constant [2 x i8] c"\0a\00"
@"str_97" = constant [9 x i8] c"get(99):\00"
@"str_98" = constant [3 x i8] c"%s\00"
@"str_99" = constant [2 x i8] c" \00"
@"str_100" = constant [4 x i8] c"%ld\00"
@"str_101" = constant [2 x i8] c"\0a\00"