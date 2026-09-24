; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
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
define i64 @"test_soma_de_ints"()
{
test_soma_de_ints_entry:
  br label %"test_soma_de_ints_body"
test_soma_de_ints_body:
  %"add" = add i64 1, 1
  %".3" = bitcast [9 x i8]* @"str_0" to i8*
  %"check_eq_call" = call i64 @"check_eq"(i64 %"add", i64 2, i8* %".3")
  %"f1" = alloca i64
  store i64 %"check_eq_call", i64* %"f1"
  %"neg" = sub i64 0, 1
  %"add.1" = add i64 %"neg", 1
  %".5" = bitcast [10 x i8]* @"str_1" to i8*
  %"check_eq_call.1" = call i64 @"check_eq"(i64 %"add.1", i64 0, i8* %".5")
  %"f2" = alloca i64
  store i64 %"check_eq_call.1", i64* %"f2"
  %".7" = bitcast [7 x i8]* @"str_2" to i8*
  %"check_ne_call" = call i64 @"check_ne"(i64 1, i64 2, i8* %".7")
  %"f3" = alloca i64
  store i64 %"check_ne_call", i64* %"f3"
  %"f1_load" = load i64, i64* %"f1"
  %"f2_load" = load i64, i64* %"f2"
  %"add.2" = add i64 %"f1_load", %"f2_load"
  %"f3_load" = load i64, i64* %"f3"
  %"add.3" = add i64 %"add.2", %"f3_load"
  ret i64 %"add.3"
}

define i64 @"test_strings"()
{
test_strings_entry:
  br label %"test_strings_body"
test_strings_body:
  %".3" = bitcast [2 x i8]* @"str_3" to i8*
  %".4" = bitcast [2 x i8]* @"str_4" to i8*
  %"sconcat_len1" = call i64 @"strlen"(i8* %".3")
  %"sconcat_len2" = call i64 @"strlen"(i8* %".4")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".3")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %".4")
  %".5" = bitcast [3 x i8]* @"str_5" to i8*
  %".6" = bitcast [7 x i8]* @"str_6" to i8*
  %"check_str_eq_call" = call i64 @"check_str_eq"(i8* %"sconcat_buf", i8* %".5", i8* %".6")
  %"f1" = alloca i64
  store i64 %"check_str_eq_call", i64* %"f1"
  %"f1_load" = load i64, i64* %"f1"
  ret i64 %"f1_load"
}

define i64 @"test_comparações"()
{
"test_comparações_entry":
  br label %"test_comparações_body"
"test_comparações_body":
  %"icmp" = icmp eq i64 1, 1
  %".3" = bitcast [7 x i8]* @"str_7" to i8*
  %"check_true_call" = call i64 @"check_true"(i1 %"icmp", i8* %".3")
  %"f1" = alloca i64
  store i64 %"check_true_call", i64* %"f1"
  %"icmp.1" = icmp eq i64 1, 2
  %".5" = bitcast [7 x i8]* @"str_8" to i8*
  %"check_false_call" = call i64 @"check_false"(i1 %"icmp.1", i8* %".5")
  %"f2" = alloca i64
  store i64 %"check_false_call", i64* %"f2"
  %"f1_load" = load i64, i64* %"f1"
  %"f2_load" = load i64, i64* %"f2"
  %"add" = add i64 %"f1_load", %"f2_load"
  ret i64 %"add"
}

define i64 @"test_falha_proposital"()
{
test_falha_proposital_entry:
  br label %"test_falha_proposital_body"
test_falha_proposital_body:
  %"add" = add i64 1, 1
  %".3" = bitcast [23 x i8]* @"str_9" to i8*
  %"check_eq_call" = call i64 @"check_eq"(i64 %"add", i64 3, i8* %".3")
  %"f1" = alloca i64
  store i64 %"check_eq_call", i64* %"f1"
  %"f1_load" = load i64, i64* %"f1"
  ret i64 %"f1_load"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define i64 @"check_eq"(i64 %".1", i64 %".2", i8* %".3")
{
check_eq_entry:
  %"actual" = alloca i64
  store i64 %".1", i64* %"actual"
  %"expected" = alloca i64
  store i64 %".2", i64* %"expected"
  %"msg" = alloca i8*
  store i8* %".3", i8** %"msg"
  br label %"check_eq_body"
check_eq_body:
  %"actual_load" = load i64, i64* %"actual"
  %"expected_load" = load i64, i64* %"expected"
  %"icmp" = icmp eq i64 %"actual_load", %"expected_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".10" = bitcast [9 x i8]* @"str_10" to i8*
  %".11" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %"msg_load" = load i8*, i8** %"msg"
  %".12" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %".13" = bitcast [3 x i8]* @"str_13" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %"msg_load")
  %".14" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".14")
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %".17" = bitcast [9 x i8]* @"str_15" to i8*
  %".18" = bitcast [3 x i8]* @"str_16" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"msg_load.1" = load i8*, i8** %"msg"
  %".19" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %"msg_load.1")
  %".21" = bitcast [12 x i8]* @"str_19" to i8*
  %".22" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %".23" = bitcast [3 x i8]* @"str_21" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".21")
  %"expected_load.1" = load i64, i64* %"expected"
  %".24" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_23" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"expected_load.1")
  %".26" = bitcast [8 x i8]* @"str_24" to i8*
  %".27" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".27")
  %".28" = bitcast [3 x i8]* @"str_26" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".26")
  %"actual_load.1" = load i64, i64* %"actual"
  %".29" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [4 x i8]* @"str_28" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".30", i64 %"actual_load.1")
  %".31" = bitcast [2 x i8]* @"str_29" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".31")
  ret i64 1
}

define i64 @"check_ne"(i64 %".1", i64 %".2", i8* %".3")
{
check_ne_entry:
  %"a" = alloca i64
  store i64 %".1", i64* %"a"
  %"b" = alloca i64
  store i64 %".2", i64* %"b"
  %"msg" = alloca i8*
  store i8* %".3", i8** %"msg"
  br label %"check_ne_body"
check_ne_body:
  %"a_load" = load i64, i64* %"a"
  %"b_load" = load i64, i64* %"b"
  %"icmp" = icmp ne i64 %"a_load", %"b_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".10" = bitcast [9 x i8]* @"str_30" to i8*
  %".11" = bitcast [3 x i8]* @"str_31" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %"msg_load" = load i8*, i8** %"msg"
  %".12" = bitcast [2 x i8]* @"str_32" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %".13" = bitcast [3 x i8]* @"str_33" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %"msg_load")
  %".14" = bitcast [2 x i8]* @"str_34" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".14")
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %".17" = bitcast [9 x i8]* @"str_35" to i8*
  %".18" = bitcast [3 x i8]* @"str_36" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"msg_load.1" = load i8*, i8** %"msg"
  %".19" = bitcast [2 x i8]* @"str_37" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [3 x i8]* @"str_38" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %"msg_load.1")
  %".21" = bitcast [15 x i8]* @"str_39" to i8*
  %".22" = bitcast [2 x i8]* @"str_40" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %".23" = bitcast [3 x i8]* @"str_41" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".21")
  %"b_load.1" = load i64, i64* %"b"
  %".24" = bitcast [2 x i8]* @"str_42" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_43" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"b_load.1")
  %".26" = bitcast [2 x i8]* @"str_44" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".26")
  ret i64 1
}

define i64 @"check_true"(i1 %".1", i8* %".2")
{
check_true_entry:
  %"cond" = alloca i1
  store i1 %".1", i1* %"cond"
  %"msg" = alloca i8*
  store i8* %".2", i8** %"msg"
  br label %"check_true_body"
check_true_body:
  %"cond_load" = load i1, i1* %"cond"
  br i1 %"cond_load", label %"if_then", label %"if_else"
if_then:
  %".8" = bitcast [9 x i8]* @"str_45" to i8*
  %".9" = bitcast [3 x i8]* @"str_46" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".9", i8* %".8")
  %"msg_load" = load i8*, i8** %"msg"
  %".10" = bitcast [2 x i8]* @"str_47" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %".11" = bitcast [3 x i8]* @"str_48" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %"msg_load")
  %".12" = bitcast [2 x i8]* @"str_49" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".12")
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %".15" = bitcast [9 x i8]* @"str_50" to i8*
  %".16" = bitcast [3 x i8]* @"str_51" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %".15")
  %"msg_load.1" = load i8*, i8** %"msg"
  %".17" = bitcast [2 x i8]* @"str_52" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [3 x i8]* @"str_53" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %"msg_load.1")
  %".19" = bitcast [16 x i8]* @"str_54" to i8*
  %".20" = bitcast [2 x i8]* @"str_55" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %".21" = bitcast [3 x i8]* @"str_56" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".19")
  %".22" = bitcast [2 x i8]* @"str_57" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  ret i64 1
}

define i64 @"check_false"(i1 %".1", i8* %".2")
{
check_false_entry:
  %"cond" = alloca i1
  store i1 %".1", i1* %"cond"
  %"msg" = alloca i8*
  store i8* %".2", i8** %"msg"
  br label %"check_false_body"
check_false_body:
  %"cond_load" = load i1, i1* %"cond"
  %"not_bool" = xor i1 %"cond_load", 1
  br i1 %"not_bool", label %"if_then", label %"if_else"
if_then:
  %".8" = bitcast [9 x i8]* @"str_58" to i8*
  %".9" = bitcast [3 x i8]* @"str_59" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".9", i8* %".8")
  %"msg_load" = load i8*, i8** %"msg"
  %".10" = bitcast [2 x i8]* @"str_60" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %".11" = bitcast [3 x i8]* @"str_61" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %"msg_load")
  %".12" = bitcast [2 x i8]* @"str_62" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".12")
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %".15" = bitcast [9 x i8]* @"str_63" to i8*
  %".16" = bitcast [3 x i8]* @"str_64" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %".15")
  %"msg_load.1" = load i8*, i8** %"msg"
  %".17" = bitcast [2 x i8]* @"str_65" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [3 x i8]* @"str_66" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %"msg_load.1")
  %".19" = bitcast [17 x i8]* @"str_67" to i8*
  %".20" = bitcast [2 x i8]* @"str_68" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %".21" = bitcast [3 x i8]* @"str_69" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".19")
  %".22" = bitcast [2 x i8]* @"str_70" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  ret i64 1
}

define i64 @"check_str_eq"(i8* %".1", i8* %".2", i8* %".3")
{
check_str_eq_entry:
  %"actual" = alloca i8*
  store i8* %".1", i8** %"actual"
  %"expected" = alloca i8*
  store i8* %".2", i8** %"expected"
  %"msg" = alloca i8*
  store i8* %".3", i8** %"msg"
  br label %"check_str_eq_body"
check_str_eq_body:
  %"actual_load" = load i8*, i8** %"actual"
  %"expected_load" = load i8*, i8** %"expected"
  %"a_null" = icmp eq i8* %"actual_load", null
  %"b_null" = icmp eq i8* %"expected_load", null
  %"either_null" = or i1 %"a_null", %"b_null"
  br i1 %"either_null", label %"strcmp_null", label %"strcmp_ok"
strcmp_null:
  %"ptr_eq" = icmp eq i8* %"actual_load", %"expected_load"
  br label %"strcmp_end"
strcmp_ok:
  %"strcmp_call" = call i32 @"strcmp"(i8* %"actual_load", i8* %"expected_load")
  %"str_eq" = icmp eq i32 %"strcmp_call", 0
  br label %"strcmp_end"
strcmp_end:
  %"str_cmp_res" = phi  i1 [%"ptr_eq", %"strcmp_null"], [%"str_eq", %"strcmp_ok"]
  br i1 %"str_cmp_res", label %"if_then", label %"if_else"
if_then:
  %".13" = bitcast [9 x i8]* @"str_71" to i8*
  %".14" = bitcast [3 x i8]* @"str_72" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %"msg_load" = load i8*, i8** %"msg"
  %".15" = bitcast [2 x i8]* @"str_73" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [3 x i8]* @"str_74" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %"msg_load")
  %".17" = bitcast [2 x i8]* @"str_75" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".17")
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %".20" = bitcast [9 x i8]* @"str_76" to i8*
  %".21" = bitcast [3 x i8]* @"str_77" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".20")
  %"msg_load.1" = load i8*, i8** %"msg"
  %".22" = bitcast [2 x i8]* @"str_78" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %".23" = bitcast [3 x i8]* @"str_79" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %"msg_load.1")
  %".24" = bitcast [12 x i8]* @"str_80" to i8*
  %".25" = bitcast [2 x i8]* @"str_81" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".25")
  %".26" = bitcast [3 x i8]* @"str_82" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".26", i8* %".24")
  %"expected_load.1" = load i8*, i8** %"expected"
  %".27" = bitcast [2 x i8]* @"str_83" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".27")
  %".28" = bitcast [3 x i8]* @"str_84" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %"expected_load.1")
  %".29" = bitcast [8 x i8]* @"str_85" to i8*
  %".30" = bitcast [2 x i8]* @"str_86" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %".31" = bitcast [3 x i8]* @"str_87" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".31", i8* %".29")
  %"actual_load.1" = load i8*, i8** %"actual"
  %".32" = bitcast [2 x i8]* @"str_88" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".32")
  %".33" = bitcast [3 x i8]* @"str_89" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %"actual_load.1")
  %".34" = bitcast [2 x i8]* @"str_90" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".34")
  ret i64 1
}

@"str_0" = constant [9 x i8] c"1+1 == 2\00"
@"str_1" = constant [10 x i8] c"-1+1 == 0\00"
@"str_2" = constant [7 x i8] c"1 != 2\00"
@"str_3" = constant [2 x i8] c"a\00"
@"str_4" = constant [2 x i8] c"b\00"
@"str_5" = constant [3 x i8] c"ab\00"
@"str_6" = constant [7 x i8] c"concat\00"
@"str_7" = constant [7 x i8] c"1 == 1\00"
@"str_8" = constant [7 x i8] c"1 != 2\00"
@"str_9" = constant [23 x i8] c"1+1 == 3 (deve falhar)\00"
@"str_10" = constant [9 x i8] c"  [PASS]\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [3 x i8] c"%s\00"
@"str_14" = constant [2 x i8] c"\0a\00"
@"str_15" = constant [9 x i8] c"  [FAIL]\00"
@"str_16" = constant [3 x i8] c"%s\00"
@"str_17" = constant [2 x i8] c" \00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [12 x i8] c"- esperado:\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [3 x i8] c"%s\00"
@"str_22" = constant [2 x i8] c" \00"
@"str_23" = constant [4 x i8] c"%ld\00"
@"str_24" = constant [8 x i8] c"obtido:\00"
@"str_25" = constant [2 x i8] c" \00"
@"str_26" = constant [3 x i8] c"%s\00"
@"str_27" = constant [2 x i8] c" \00"
@"str_28" = constant [4 x i8] c"%ld\00"
@"str_29" = constant [2 x i8] c"\0a\00"
@"str_30" = constant [9 x i8] c"  [PASS]\00"
@"str_31" = constant [3 x i8] c"%s\00"
@"str_32" = constant [2 x i8] c" \00"
@"str_33" = constant [3 x i8] c"%s\00"
@"str_34" = constant [2 x i8] c"\0a\00"
@"str_35" = constant [9 x i8] c"  [FAIL]\00"
@"str_36" = constant [3 x i8] c"%s\00"
@"str_37" = constant [2 x i8] c" \00"
@"str_38" = constant [3 x i8] c"%s\00"
@"str_39" = constant [15 x i8] c"- esperado != \00"
@"str_40" = constant [2 x i8] c" \00"
@"str_41" = constant [3 x i8] c"%s\00"
@"str_42" = constant [2 x i8] c" \00"
@"str_43" = constant [4 x i8] c"%ld\00"
@"str_44" = constant [2 x i8] c"\0a\00"
@"str_45" = constant [9 x i8] c"  [PASS]\00"
@"str_46" = constant [3 x i8] c"%s\00"
@"str_47" = constant [2 x i8] c" \00"
@"str_48" = constant [3 x i8] c"%s\00"
@"str_49" = constant [2 x i8] c"\0a\00"
@"str_50" = constant [9 x i8] c"  [FAIL]\00"
@"str_51" = constant [3 x i8] c"%s\00"
@"str_52" = constant [2 x i8] c" \00"
@"str_53" = constant [3 x i8] c"%s\00"
@"str_54" = constant [16 x i8] c"- esperado true\00"
@"str_55" = constant [2 x i8] c" \00"
@"str_56" = constant [3 x i8] c"%s\00"
@"str_57" = constant [2 x i8] c"\0a\00"
@"str_58" = constant [9 x i8] c"  [PASS]\00"
@"str_59" = constant [3 x i8] c"%s\00"
@"str_60" = constant [2 x i8] c" \00"
@"str_61" = constant [3 x i8] c"%s\00"
@"str_62" = constant [2 x i8] c"\0a\00"
@"str_63" = constant [9 x i8] c"  [FAIL]\00"
@"str_64" = constant [3 x i8] c"%s\00"
@"str_65" = constant [2 x i8] c" \00"
@"str_66" = constant [3 x i8] c"%s\00"
@"str_67" = constant [17 x i8] c"- esperado false\00"
@"str_68" = constant [2 x i8] c" \00"
@"str_69" = constant [3 x i8] c"%s\00"
@"str_70" = constant [2 x i8] c"\0a\00"
@"str_71" = constant [9 x i8] c"  [PASS]\00"
@"str_72" = constant [3 x i8] c"%s\00"
@"str_73" = constant [2 x i8] c" \00"
@"str_74" = constant [3 x i8] c"%s\00"
@"str_75" = constant [2 x i8] c"\0a\00"
@"str_76" = constant [9 x i8] c"  [FAIL]\00"
@"str_77" = constant [3 x i8] c"%s\00"
@"str_78" = constant [2 x i8] c" \00"
@"str_79" = constant [3 x i8] c"%s\00"
@"str_80" = constant [12 x i8] c"- esperado:\00"
@"str_81" = constant [2 x i8] c" \00"
@"str_82" = constant [3 x i8] c"%s\00"
@"str_83" = constant [2 x i8] c" \00"
@"str_84" = constant [3 x i8] c"%s\00"
@"str_85" = constant [8 x i8] c"obtido:\00"
@"str_86" = constant [2 x i8] c" \00"
@"str_87" = constant [3 x i8] c"%s\00"
@"str_88" = constant [2 x i8] c" \00"
@"str_89" = constant [3 x i8] c"%s\00"
@"str_90" = constant [2 x i8] c"\0a\00"