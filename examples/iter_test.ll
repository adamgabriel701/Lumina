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
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"n" = alloca i64
  store i64 5, i64* %"n"
  %"n_load" = load i64, i64* %"n"
  %"alloc_size" = mul i64 %"n_load", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"arr" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"arr"
  %"arr_load" = load i64*, i64** %"arr"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load", i64 0
  store i64 1, i64* %"idx_ptr"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"idx_ptr.1" = getelementptr i64, i64* %"arr_load.1", i64 1
  store i64 2, i64* %"idx_ptr.1"
  %"arr_load.2" = load i64*, i64** %"arr"
  %"idx_ptr.2" = getelementptr i64, i64* %"arr_load.2", i64 2
  store i64 3, i64* %"idx_ptr.2"
  %"arr_load.3" = load i64*, i64** %"arr"
  %"idx_ptr.3" = getelementptr i64, i64* %"arr_load.3", i64 3
  store i64 4, i64* %"idx_ptr.3"
  %"arr_load.4" = load i64*, i64** %"arr"
  %"idx_ptr.4" = getelementptr i64, i64* %"arr_load.4", i64 4
  store i64 5, i64* %"idx_ptr.4"
  %".14" = bitcast [23 x i8]* @"str_0" to i8*
  %".15" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".15", i8* %".14")
  %".16" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [6 x i8]* @"str_3" to i8*
  %".18" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"arr_load.5" = load i64*, i64** %"arr"
  %"n_load.1" = load i64, i64* %"n"
  %"sum_call" = call i64 @"sum"(i64* %"arr_load.5", i64 %"n_load.1")
  %".19" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"sum_call")
  %".21" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [9 x i8]* @"str_8" to i8*
  %".23" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"arr_load.6" = load i64*, i64** %"arr"
  %"n_load.2" = load i64, i64* %"n"
  %"product_call" = call i64 @"product"(i64* %"arr_load.6", i64 %"n_load.2")
  %".24" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"product_call")
  %".26" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [5 x i8]* @"str_13" to i8*
  %".28" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %"arr_load.7" = load i64*, i64** %"arr"
  %"n_load.3" = load i64, i64* %"n"
  %"min_call" = call i64 @"min"(i64* %"arr_load.7", i64 %"n_load.3")
  %".29" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".30", i64 %"min_call")
  %".31" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [5 x i8]* @"str_18" to i8*
  %".33" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %"arr_load.8" = load i64*, i64** %"arr"
  %"n_load.4" = load i64, i64* %"n"
  %"max_call" = call i64 @"max"(i64* %"arr_load.8", i64 %"n_load.4")
  %".34" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".35", i64 %"max_call")
  %".36" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %".37" = bitcast [12 x i8]* @"str_23" to i8*
  %".38" = bitcast [3 x i8]* @"str_24" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".38", i8* %".37")
  %".39" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".39")
  %"arr_load.9" = load i64*, i64** %"arr"
  %"n_load.5" = load i64, i64* %"n"
  %"closure_env_0" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_0" = bitcast i8* %"closure_env_0" to {}*
  %"closure___closure_0" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp" = bitcast i8* %"closure___closure_0" to i8**
  %"fn_as_ptr" = bitcast i64 (i8*, i64)* @"__closure_0" to i8*
  store i8* %"fn_as_ptr", i8** %"closure_i8pp"
  %"env_slot" = getelementptr i8*, i8** %"closure_i8pp", i64 1
  store i8* %"closure_env_0", i8** %"env_slot"
  %"map_call" = call i64* @"map"(i64* %"arr_load.9", i64 %"n_load.5", i8* %"closure___closure_0")
  %"dobrados" = alloca i64*
  store i64* %"map_call", i64** %"dobrados"
  %".43" = bitcast [16 x i8]* @"str_26" to i8*
  %".44" = bitcast [3 x i8]* @"str_27" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".44", i8* %".43")
  %"dobrados_load" = load i64*, i64** %"dobrados"
  %"n_load.6" = load i64, i64* %"n"
  %"sum_call.1" = call i64 @"sum"(i64* %"dobrados_load", i64 %"n_load.6")
  %".45" = bitcast [2 x i8]* @"str_28" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".45")
  %".46" = bitcast [4 x i8]* @"str_29" to i8*
  %"print_call.11" = call i32 (i8*, ...) @"printf"(i8* %".46", i64 %"sum_call.1")
  %".47" = bitcast [2 x i8]* @"str_30" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".47")
  %".48" = bitcast [15 x i8]* @"str_31" to i8*
  %".49" = bitcast [3 x i8]* @"str_32" to i8*
  %"print_call.12" = call i32 (i8*, ...) @"printf"(i8* %".49", i8* %".48")
  %".50" = bitcast [2 x i8]* @"str_33" to i8*
  %"print_nl.7" = call i32 (i8*, ...) @"printf"(i8* %".50")
  %"arr_load.10" = load i64*, i64** %"arr"
  %"n_load.7" = load i64, i64* %"n"
  %"closure_env_1" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_1" = bitcast i8* %"closure_env_1" to {}*
  %"closure___closure_1" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp.1" = bitcast i8* %"closure___closure_1" to i8**
  %"fn_as_ptr.1" = bitcast i64 (i8*, i64)* @"__closure_1" to i8*
  store i8* %"fn_as_ptr.1", i8** %"closure_i8pp.1"
  %"env_slot.1" = getelementptr i8*, i8** %"closure_i8pp.1", i64 1
  store i8* %"closure_env_1", i8** %"env_slot.1"
  %"filter_call" = call i64* @"filter"(i64* %"arr_load.10", i64 %"n_load.7", i8* %"closure___closure_1")
  %"pares" = alloca i64*
  store i64* %"filter_call", i64** %"pares"
  %"arr_load.11" = load i64*, i64** %"arr"
  %"n_load.8" = load i64, i64* %"n"
  %"closure_env_2" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_2" = bitcast i8* %"closure_env_2" to {}*
  %"closure___closure_2" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp.2" = bitcast i8* %"closure___closure_2" to i8**
  %"fn_as_ptr.2" = bitcast i64 (i8*, i64)* @"__closure_2" to i8*
  store i8* %"fn_as_ptr.2", i8** %"closure_i8pp.2"
  %"env_slot.2" = getelementptr i8*, i8** %"closure_i8pp.2", i64 1
  store i8* %"closure_env_2", i8** %"env_slot.2"
  %"count_if_call" = call i64 @"count_if"(i64* %"arr_load.11", i64 %"n_load.8", i8* %"closure___closure_2")
  %"npares" = alloca i64
  store i64 %"count_if_call", i64* %"npares"
  %".57" = bitcast [21 x i8]* @"str_34" to i8*
  %".58" = bitcast [3 x i8]* @"str_35" to i8*
  %"print_call.13" = call i32 (i8*, ...) @"printf"(i8* %".58", i8* %".57")
  %"npares_load" = load i64, i64* %"npares"
  %".59" = bitcast [2 x i8]* @"str_36" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".59")
  %".60" = bitcast [4 x i8]* @"str_37" to i8*
  %"print_call.14" = call i32 (i8*, ...) @"printf"(i8* %".60", i64 %"npares_load")
  %".61" = bitcast [2 x i8]* @"str_38" to i8*
  %"print_nl.8" = call i32 (i8*, ...) @"printf"(i8* %".61")
  %".62" = bitcast [16 x i8]* @"str_39" to i8*
  %".63" = bitcast [3 x i8]* @"str_40" to i8*
  %"print_call.15" = call i32 (i8*, ...) @"printf"(i8* %".63", i8* %".62")
  %"pares_load" = load i64*, i64** %"pares"
  %"npares_load.1" = load i64, i64* %"npares"
  %"sum_call.2" = call i64 @"sum"(i64* %"pares_load", i64 %"npares_load.1")
  %".64" = bitcast [2 x i8]* @"str_41" to i8*
  %"print_sep.6" = call i32 (i8*, ...) @"printf"(i8* %".64")
  %".65" = bitcast [4 x i8]* @"str_42" to i8*
  %"print_call.16" = call i32 (i8*, ...) @"printf"(i8* %".65", i64 %"sum_call.2")
  %".66" = bitcast [2 x i8]* @"str_43" to i8*
  %"print_nl.9" = call i32 (i8*, ...) @"printf"(i8* %".66")
  %".67" = bitcast [18 x i8]* @"str_44" to i8*
  %".68" = bitcast [3 x i8]* @"str_45" to i8*
  %"print_call.17" = call i32 (i8*, ...) @"printf"(i8* %".68", i8* %".67")
  %".69" = bitcast [2 x i8]* @"str_46" to i8*
  %"print_nl.10" = call i32 (i8*, ...) @"printf"(i8* %".69")
  %".70" = bitcast [17 x i8]* @"str_47" to i8*
  %".71" = bitcast [3 x i8]* @"str_48" to i8*
  %"print_call.18" = call i32 (i8*, ...) @"printf"(i8* %".71", i8* %".70")
  %"arr_load.12" = load i64*, i64** %"arr"
  %"n_load.9" = load i64, i64* %"n"
  %"closure_env_3" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_3" = bitcast i8* %"closure_env_3" to {}*
  %"closure___closure_3" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp.3" = bitcast i8* %"closure___closure_3" to i8**
  %"fn_as_ptr.3" = bitcast i64 (i8*, i64)* @"__closure_3" to i8*
  store i8* %"fn_as_ptr.3", i8** %"closure_i8pp.3"
  %"env_slot.3" = getelementptr i8*, i8** %"closure_i8pp.3", i64 1
  store i8* %"closure_env_3", i8** %"env_slot.3"
  %"all_call" = call i64 @"all"(i64* %"arr_load.12", i64 %"n_load.9", i8* %"closure___closure_3")
  %".74" = bitcast [2 x i8]* @"str_49" to i8*
  %"print_sep.7" = call i32 (i8*, ...) @"printf"(i8* %".74")
  %".75" = bitcast [4 x i8]* @"str_50" to i8*
  %"print_call.19" = call i32 (i8*, ...) @"printf"(i8* %".75", i64 %"all_call")
  %".76" = bitcast [2 x i8]* @"str_51" to i8*
  %"print_nl.11" = call i32 (i8*, ...) @"printf"(i8* %".76")
  %".77" = bitcast [11 x i8]* @"str_52" to i8*
  %".78" = bitcast [3 x i8]* @"str_53" to i8*
  %"print_call.20" = call i32 (i8*, ...) @"printf"(i8* %".78", i8* %".77")
  %"arr_load.13" = load i64*, i64** %"arr"
  %"n_load.10" = load i64, i64* %"n"
  %"closure_env_4" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_4" = bitcast i8* %"closure_env_4" to {}*
  %"closure___closure_4" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp.4" = bitcast i8* %"closure___closure_4" to i8**
  %"fn_as_ptr.4" = bitcast i64 (i8*, i64)* @"__closure_4" to i8*
  store i8* %"fn_as_ptr.4", i8** %"closure_i8pp.4"
  %"env_slot.4" = getelementptr i8*, i8** %"closure_i8pp.4", i64 1
  store i8* %"closure_env_4", i8** %"env_slot.4"
  %"any_call" = call i64 @"any"(i64* %"arr_load.13", i64 %"n_load.10", i8* %"closure___closure_4")
  %".81" = bitcast [2 x i8]* @"str_54" to i8*
  %"print_sep.8" = call i32 (i8*, ...) @"printf"(i8* %".81")
  %".82" = bitcast [4 x i8]* @"str_55" to i8*
  %"print_call.21" = call i32 (i8*, ...) @"printf"(i8* %".82", i64 %"any_call")
  %".83" = bitcast [2 x i8]* @"str_56" to i8*
  %"print_nl.12" = call i32 (i8*, ...) @"printf"(i8* %".83")
  %".84" = bitcast [19 x i8]* @"str_57" to i8*
  %".85" = bitcast [3 x i8]* @"str_58" to i8*
  %"print_call.22" = call i32 (i8*, ...) @"printf"(i8* %".85", i8* %".84")
  %".86" = bitcast [2 x i8]* @"str_59" to i8*
  %"print_nl.13" = call i32 (i8*, ...) @"printf"(i8* %".86")
  %"arr_load.14" = load i64*, i64** %"arr"
  %"n_load.11" = load i64, i64* %"n"
  %"closure_env_5" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_5" = bitcast i8* %"closure_env_5" to {}*
  %"closure___closure_5" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp.5" = bitcast i8* %"closure___closure_5" to i8**
  %"fn_as_ptr.5" = bitcast i64 (i8*, i64)* @"__closure_5" to i8*
  store i8* %"fn_as_ptr.5", i8** %"closure_i8pp.5"
  %"env_slot.5" = getelementptr i8*, i8** %"closure_i8pp.5", i64 1
  store i8* %"closure_env_5", i8** %"env_slot.5"
  %"find_index_call" = call i64 @"find_index"(i64* %"arr_load.14", i64 %"n_load.11", i8* %"closure___closure_5")
  %"idx" = alloca i64
  store i64 %"find_index_call", i64* %"idx"
  %".90" = bitcast [14 x i8]* @"str_60" to i8*
  %".91" = bitcast [3 x i8]* @"str_61" to i8*
  %"print_call.23" = call i32 (i8*, ...) @"printf"(i8* %".91", i8* %".90")
  %"idx_load" = load i64, i64* %"idx"
  %".92" = bitcast [2 x i8]* @"str_62" to i8*
  %"print_sep.9" = call i32 (i8*, ...) @"printf"(i8* %".92")
  %".93" = bitcast [4 x i8]* @"str_63" to i8*
  %"print_call.24" = call i32 (i8*, ...) @"printf"(i8* %".93", i64 %"idx_load")
  %".94" = bitcast [2 x i8]* @"str_64" to i8*
  %"print_nl.14" = call i32 (i8*, ...) @"printf"(i8* %".94")
  %".95" = bitcast [17 x i8]* @"str_65" to i8*
  %".96" = bitcast [3 x i8]* @"str_66" to i8*
  %"print_call.25" = call i32 (i8*, ...) @"printf"(i8* %".96", i8* %".95")
  %".97" = bitcast [2 x i8]* @"str_67" to i8*
  %"print_nl.15" = call i32 (i8*, ...) @"printf"(i8* %".97")
  %"arr_load.15" = load i64*, i64** %"arr"
  %"n_load.12" = load i64, i64* %"n"
  %"closure_env_6" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_6" = bitcast i8* %"closure_env_6" to {}*
  %"closure___closure_6" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp.6" = bitcast i8* %"closure___closure_6" to i8**
  %"fn_as_ptr.6" = bitcast i64 (i8*, i64)* @"__closure_6" to i8*
  store i8* %"fn_as_ptr.6", i8** %"closure_i8pp.6"
  %"env_slot.6" = getelementptr i8*, i8** %"closure_i8pp.6", i64 1
  store i8* %"closure_env_6", i8** %"env_slot.6"
  call void @"for_each"(i64* %"arr_load.15", i64 %"n_load.12", i8* %"closure___closure_6")
  %".100" = bitcast [17 x i8]* @"str_68" to i8*
  %".101" = bitcast [3 x i8]* @"str_69" to i8*
  %"print_call.26" = call i32 (i8*, ...) @"printf"(i8* %".101", i8* %".100")
  %"arr_load.16" = load i64*, i64** %"arr"
  %"n_load.13" = load i64, i64* %"n"
  %"sum_call.3" = call i64 @"sum"(i64* %"arr_load.16", i64 %"n_load.13")
  %".102" = bitcast [2 x i8]* @"str_70" to i8*
  %"print_sep.10" = call i32 (i8*, ...) @"printf"(i8* %".102")
  %".103" = bitcast [4 x i8]* @"str_71" to i8*
  %"print_call.27" = call i32 (i8*, ...) @"printf"(i8* %".103", i64 %"sum_call.3")
  %".104" = bitcast [2 x i8]* @"str_72" to i8*
  %"print_nl.16" = call i32 (i8*, ...) @"printf"(i8* %".104")
  %".105" = bitcast [16 x i8]* @"str_73" to i8*
  %".106" = bitcast [3 x i8]* @"str_74" to i8*
  %"print_call.28" = call i32 (i8*, ...) @"printf"(i8* %".106", i8* %".105")
  %".107" = bitcast [2 x i8]* @"str_75" to i8*
  %"print_nl.17" = call i32 (i8*, ...) @"printf"(i8* %".107")
  %"arr_load.17" = load i64*, i64** %"arr"
  %"n_load.14" = load i64, i64* %"n"
  call void @"reverse"(i64* %"arr_load.17", i64 %"n_load.14")
  %".108" = bitcast [33 x i8]* @"str_76" to i8*
  %".109" = bitcast [3 x i8]* @"str_77" to i8*
  %"print_call.29" = call i32 (i8*, ...) @"printf"(i8* %".109", i8* %".108")
  %"arr_load.18" = load i64*, i64** %"arr"
  %".110" = getelementptr i64, i64* %"arr_load.18", i64 0
  %"ptr_idx_load" = load i64, i64* %".110"
  %".111" = bitcast [2 x i8]* @"str_78" to i8*
  %"print_sep.11" = call i32 (i8*, ...) @"printf"(i8* %".111")
  %".112" = bitcast [4 x i8]* @"str_79" to i8*
  %"print_call.30" = call i32 (i8*, ...) @"printf"(i8* %".112", i64 %"ptr_idx_load")
  %".113" = bitcast [2 x i8]* @"str_80" to i8*
  %"print_nl.18" = call i32 (i8*, ...) @"printf"(i8* %".113")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define i64 @"count_if"(i64* %".1", i64 %".2", i8* %".3")
{
count_if_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"pred" = alloca i8*
  store i8* %".3", i8** %"pred"
  br label %"count_if_body"
count_if_body:
  %"count" = alloca i64
  store i64 0, i64* %"count"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"pred_closure" = load i8*, i8** %"pred"
  %"pred_c8pp" = bitcast i8* %"pred_closure" to i8**
  %"pred_fn" = load i8*, i8** %"pred_c8pp"
  %"pred_env_slot" = getelementptr i8*, i8** %"pred_c8pp", i64 1
  %"pred_env" = load i8*, i8** %"pred_env_slot"
  %"pred_cast" = bitcast i8* %"pred_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".13" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".13"
  %"pred_call" = call i64 %"pred_cast"(i8* %"pred_env", i64 %"ptr_idx_load")
  %"icmp.1" = icmp ne i64 %"pred_call", 0
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"count_load.1" = load i64, i64* %"count"
  ret i64 %"count_load.1"
if_then:
  %"count_load" = load i64, i64* %"count"
  %"add" = add i64 %"count_load", 1
  store i64 %"add", i64* %"count"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
}

define i64* @"map"(i64* %".1", i64 %".2", i8* %".3")
{
map_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"f" = alloca i8*
  store i8* %".3", i8** %"f"
  br label %"map_body"
map_body:
  %"n_load" = load i64, i64* %"n"
  %"alloc_size" = mul i64 %"n_load", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"out" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"out"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load.1" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"f_closure" = load i8*, i8** %"f"
  %"f_c8pp" = bitcast i8* %"f_closure" to i8**
  %"f_fn" = load i8*, i8** %"f_c8pp"
  %"f_env_slot" = getelementptr i8*, i8** %"f_c8pp", i64 1
  %"f_env" = load i8*, i8** %"f_env_slot"
  %"f_cast" = bitcast i8* %"f_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".13" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".13"
  %"f_call" = call i64 %"f_cast"(i8* %"f_env", i64 %"ptr_idx_load")
  %"out_load" = load i64*, i64** %"out"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"out_load", i64 %"i_load.2"
  store i64 %"f_call", i64* %"idx_ptr"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"out_load.1" = load i64*, i64** %"out"
  ret i64* %"out_load.1"
}

define i64* @"filter"(i64* %".1", i64 %".2", i8* %".3")
{
filter_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"pred" = alloca i8*
  store i8* %".3", i8** %"pred"
  br label %"filter_body"
filter_body:
  %"n_load" = load i64, i64* %"n"
  %"alloc_size" = mul i64 %"n_load", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"out" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"out"
  %"count" = alloca i64
  store i64 0, i64* %"count"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load.1" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"pred_closure" = load i8*, i8** %"pred"
  %"pred_c8pp" = bitcast i8* %"pred_closure" to i8**
  %"pred_fn" = load i8*, i8** %"pred_c8pp"
  %"pred_env_slot" = getelementptr i8*, i8** %"pred_c8pp", i64 1
  %"pred_env" = load i8*, i8** %"pred_env_slot"
  %"pred_cast" = bitcast i8* %"pred_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".14" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".14"
  %"pred_call" = call i64 %"pred_cast"(i8* %"pred_env", i64 %"ptr_idx_load")
  %"icmp.1" = icmp ne i64 %"pred_call", 0
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"out_load.1" = load i64*, i64** %"out"
  ret i64* %"out_load.1"
if_then:
  %"arr_load.1" = load i64*, i64** %"arr"
  %"i_load.2" = load i64, i64* %"i"
  %".16" = getelementptr i64, i64* %"arr_load.1", i64 %"i_load.2"
  %"ptr_idx_load.1" = load i64, i64* %".16"
  %"out_load" = load i64*, i64** %"out"
  %"count_load" = load i64, i64* %"count"
  %"idx_ptr" = getelementptr i64, i64* %"out_load", i64 %"count_load"
  store i64 %"ptr_idx_load.1", i64* %"idx_ptr"
  %"count_load.1" = load i64, i64* %"count"
  %"add" = add i64 %"count_load.1", 1
  store i64 %"add", i64* %"count"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
}

define i64 @"sum_by"(i64* %".1", i64 %".2", i8* %".3")
{
sum_by_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"f" = alloca i8*
  store i8* %".3", i8** %"f"
  br label %"sum_by_body"
sum_by_body:
  %"total" = alloca i64
  store i64 0, i64* %"total"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"total_load" = load i64, i64* %"total"
  %"f_closure" = load i8*, i8** %"f"
  %"f_c8pp" = bitcast i8* %"f_closure" to i8**
  %"f_fn" = load i8*, i8** %"f_c8pp"
  %"f_env_slot" = getelementptr i8*, i8** %"f_c8pp", i64 1
  %"f_env" = load i8*, i8** %"f_env_slot"
  %"f_cast" = bitcast i8* %"f_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".13" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".13"
  %"f_call" = call i64 %"f_cast"(i8* %"f_env", i64 %"ptr_idx_load")
  %"add" = add i64 %"total_load", %"f_call"
  store i64 %"add", i64* %"total"
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %"total_load.1" = load i64, i64* %"total"
  ret i64 %"total_load.1"
}

define i64 @"all"(i64* %".1", i64 %".2", i8* %".3")
{
all_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"pred" = alloca i8*
  store i8* %".3", i8** %"pred"
  br label %"all_body"
all_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"pred_closure" = load i8*, i8** %"pred"
  %"pred_c8pp" = bitcast i8* %"pred_closure" to i8**
  %"pred_fn" = load i8*, i8** %"pred_c8pp"
  %"pred_env_slot" = getelementptr i8*, i8** %"pred_c8pp", i64 1
  %"pred_env" = load i8*, i8** %"pred_env_slot"
  %"pred_cast" = bitcast i8* %"pred_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".12"
  %"pred_call" = call i64 %"pred_cast"(i8* %"pred_env", i64 %"ptr_idx_load")
  %"icmp.1" = icmp eq i64 %"pred_call", 0
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 1
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i64 @"any"(i64* %".1", i64 %".2", i8* %".3")
{
any_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"pred" = alloca i8*
  store i8* %".3", i8** %"pred"
  br label %"any_body"
any_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"pred_closure" = load i8*, i8** %"pred"
  %"pred_c8pp" = bitcast i8* %"pred_closure" to i8**
  %"pred_fn" = load i8*, i8** %"pred_c8pp"
  %"pred_env_slot" = getelementptr i8*, i8** %"pred_c8pp", i64 1
  %"pred_env" = load i8*, i8** %"pred_env_slot"
  %"pred_cast" = bitcast i8* %"pred_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".12"
  %"pred_call" = call i64 %"pred_cast"(i8* %"pred_env", i64 %"ptr_idx_load")
  %"icmp.1" = icmp ne i64 %"pred_call", 0
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 0
if_then:
  ret i64 1
if_else:
  br label %"if_end"
if_end:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i64 @"find_index"(i64* %".1", i64 %".2", i8* %".3")
{
find_index_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"pred" = alloca i8*
  store i8* %".3", i8** %"pred"
  br label %"find_index_body"
find_index_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"pred_closure" = load i8*, i8** %"pred"
  %"pred_c8pp" = bitcast i8* %"pred_closure" to i8**
  %"pred_fn" = load i8*, i8** %"pred_c8pp"
  %"pred_env_slot" = getelementptr i8*, i8** %"pred_c8pp", i64 1
  %"pred_env" = load i8*, i8** %"pred_env_slot"
  %"pred_cast" = bitcast i8* %"pred_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".12"
  %"pred_call" = call i64 %"pred_cast"(i8* %"pred_env", i64 %"ptr_idx_load")
  %"icmp.1" = icmp ne i64 %"pred_call", 0
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
if_then:
  %"i_load.2" = load i64, i64* %"i"
  ret i64 %"i_load.2"
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i64 @"sum"(i64* %".1", i64 %".2")
{
sum_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  br label %"sum_body"
sum_body:
  %"total" = alloca i64
  store i64 0, i64* %"total"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"total_load" = load i64, i64* %"total"
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".11" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".11"
  %"add" = add i64 %"total_load", %"ptr_idx_load"
  store i64 %"add", i64* %"total"
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %"total_load.1" = load i64, i64* %"total"
  ret i64 %"total_load.1"
}

define i64 @"product"(i64* %".1", i64 %".2")
{
product_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  br label %"product_body"
product_body:
  %"result" = alloca i64
  store i64 1, i64* %"result"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"result_load" = load i64, i64* %"result"
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".11" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".11"
  %"mul" = mul i64 %"result_load", %"ptr_idx_load"
  store i64 %"mul", i64* %"result"
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"result_load.1" = load i64, i64* %"result"
  ret i64 %"result_load.1"
}

define i64 @"min"(i64* %".1", i64 %".2")
{
min_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  br label %"min_body"
min_body:
  %"arr_load" = load i64*, i64** %"arr"
  %".7" = getelementptr i64, i64* %"arr_load", i64 0
  %"ptr_idx_load" = load i64, i64* %".7"
  %"result" = alloca i64
  store i64 %"ptr_idx_load", i64* %"result"
  %"i" = alloca i64
  store i64 1, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"arr_load.1" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i64, i64* %"arr_load.1", i64 %"i_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".12"
  %"result_load" = load i64, i64* %"result"
  %"icmp.1" = icmp slt i64 %"ptr_idx_load.1", %"result_load"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"result_load.1" = load i64, i64* %"result"
  ret i64 %"result_load.1"
if_then:
  %"arr_load.2" = load i64*, i64** %"arr"
  %"i_load.2" = load i64, i64* %"i"
  %".14" = getelementptr i64, i64* %"arr_load.2", i64 %"i_load.2"
  %"ptr_idx_load.2" = load i64, i64* %".14"
  store i64 %"ptr_idx_load.2", i64* %"result"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i64 @"max"(i64* %".1", i64 %".2")
{
max_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  br label %"max_body"
max_body:
  %"arr_load" = load i64*, i64** %"arr"
  %".7" = getelementptr i64, i64* %"arr_load", i64 0
  %"ptr_idx_load" = load i64, i64* %".7"
  %"result" = alloca i64
  store i64 %"ptr_idx_load", i64* %"result"
  %"i" = alloca i64
  store i64 1, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"arr_load.1" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i64, i64* %"arr_load.1", i64 %"i_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".12"
  %"result_load" = load i64, i64* %"result"
  %"icmp.1" = icmp sgt i64 %"ptr_idx_load.1", %"result_load"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"result_load.1" = load i64, i64* %"result"
  ret i64 %"result_load.1"
if_then:
  %"arr_load.2" = load i64*, i64** %"arr"
  %"i_load.2" = load i64, i64* %"i"
  %".14" = getelementptr i64, i64* %"arr_load.2", i64 %"i_load.2"
  %"ptr_idx_load.2" = load i64, i64* %".14"
  store i64 %"ptr_idx_load.2", i64* %"result"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i64* @"copy"(i64* %".1", i64 %".2")
{
copy_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  br label %"copy_body"
copy_body:
  %"n_load" = load i64, i64* %"n"
  %"alloc_size" = mul i64 %"n_load", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"out" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"out"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load.1" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".11" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".11"
  %"out_load" = load i64*, i64** %"out"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"out_load", i64 %"i_load.2"
  store i64 %"ptr_idx_load", i64* %"idx_ptr"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"out_load.1" = load i64*, i64** %"out"
  ret i64* %"out_load.1"
}

define void @"fill"(i64* %".1", i64 %".2", i64 %".3")
{
fill_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"value" = alloca i64
  store i64 %".3", i64* %"value"
  br label %"fill_body"
fill_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"value_load" = load i64, i64* %"value"
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  store i64 %"value_load", i64* %"idx_ptr"
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  ret void
}

define void @"for_each"(i64* %".1", i64 %".2", i8* %".3")
{
for_each_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  %"f" = alloca i8*
  store i8* %".3", i8** %"f"
  br label %"for_each_body"
for_each_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"f_closure" = load i8*, i8** %"f"
  %"f_c8pp" = bitcast i8* %"f_closure" to i8**
  %"f_fn" = load i8*, i8** %"f_c8pp"
  %"f_env_slot" = getelementptr i8*, i8** %"f_c8pp", i64 1
  %"f_env" = load i8*, i8** %"f_env_slot"
  %"f_cast" = bitcast i8* %"f_fn" to i64 (i8*, i64)*
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".12"
  %"f_call" = call i64 %"f_cast"(i8* %"f_env", i64 %"ptr_idx_load")
  %"arr_load.1" = load i64*, i64** %"arr"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load.1", i64 %"i_load.2"
  store i64 %"f_call", i64* %"idx_ptr"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  ret void
}

define void @"reverse"(i64* %".1", i64 %".2")
{
reverse_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"n" = alloca i64
  store i64 %".2", i64* %"n"
  br label %"reverse_body"
reverse_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"sub" = sub i64 %"n_load", 1
  %"j" = alloca i64
  store i64 %"sub", i64* %"j"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"j_load" = load i64, i64* %"j"
  %"icmp" = icmp slt i64 %"i_load", %"j_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".11" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".11"
  %"tmp" = alloca i64
  store i64 %"ptr_idx_load", i64* %"tmp"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"j_load.1" = load i64, i64* %"j"
  %".13" = getelementptr i64, i64* %"arr_load.1", i64 %"j_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".13"
  %"arr_load.2" = load i64*, i64** %"arr"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load.2", i64 %"i_load.2"
  store i64 %"ptr_idx_load.1", i64* %"idx_ptr"
  %"tmp_load" = load i64, i64* %"tmp"
  %"arr_load.3" = load i64*, i64** %"arr"
  %"j_load.2" = load i64, i64* %"j"
  %"idx_ptr.1" = getelementptr i64, i64* %"arr_load.3", i64 %"j_load.2"
  store i64 %"tmp_load", i64* %"idx_ptr.1"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  %"j_load.3" = load i64, i64* %"j"
  %"sub.1" = sub i64 %"j_load.3", 1
  store i64 %"sub.1", i64* %"j"
  br label %"while_cond"
while_end:
  ret void
}

@"str_0" = constant [23 x i8] c"=== Array original ===\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [6 x i8] c"Soma:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [9 x i8] c"Produto:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [5 x i8] c"Min:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [5 x i8] c"Max:\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"
@"str_23" = constant [12 x i8] c"=== map ===\00"
@"str_24" = constant [3 x i8] c"%s\00"
@"str_25" = constant [2 x i8] c"\0a\00"
define i64 @"__closure_0"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"mul" = mul i64 %"x_load", 2
  ret i64 %"mul"
}

@"str_26" = constant [16 x i8] c"Dobrados somam:\00"
@"str_27" = constant [3 x i8] c"%s\00"
@"str_28" = constant [2 x i8] c" \00"
@"str_29" = constant [4 x i8] c"%ld\00"
@"str_30" = constant [2 x i8] c"\0a\00"
@"str_31" = constant [15 x i8] c"=== filter ===\00"
@"str_32" = constant [3 x i8] c"%s\00"
@"str_33" = constant [2 x i8] c"\0a\00"
define i64 @"__closure_1"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"mod" = srem i64 %"x_load", 2
  %"icmp" = icmp eq i64 %"mod", 0
  %"closure_ret_zext" = zext i1 %"icmp" to i64
  ret i64 %"closure_ret_zext"
}

define i64 @"__closure_2"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"mod" = srem i64 %"x_load", 2
  %"icmp" = icmp eq i64 %"mod", 0
  %"closure_ret_zext" = zext i1 %"icmp" to i64
  ret i64 %"closure_ret_zext"
}

@"str_34" = constant [21 x i8] c"Quantidade de pares:\00"
@"str_35" = constant [3 x i8] c"%s\00"
@"str_36" = constant [2 x i8] c" \00"
@"str_37" = constant [4 x i8] c"%ld\00"
@"str_38" = constant [2 x i8] c"\0a\00"
@"str_39" = constant [16 x i8] c"Soma dos pares:\00"
@"str_40" = constant [3 x i8] c"%s\00"
@"str_41" = constant [2 x i8] c" \00"
@"str_42" = constant [4 x i8] c"%ld\00"
@"str_43" = constant [2 x i8] c"\0a\00"
@"str_44" = constant [18 x i8] c"=== all / any ===\00"
@"str_45" = constant [3 x i8] c"%s\00"
@"str_46" = constant [2 x i8] c"\0a\00"
@"str_47" = constant [17 x i8] c"Todos positivos?\00"
@"str_48" = constant [3 x i8] c"%s\00"
define i64 @"__closure_3"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"icmp" = icmp sgt i64 %"x_load", 0
  %"closure_ret_zext" = zext i1 %"icmp" to i64
  ret i64 %"closure_ret_zext"
}

@"str_49" = constant [2 x i8] c" \00"
@"str_50" = constant [4 x i8] c"%ld\00"
@"str_51" = constant [2 x i8] c"\0a\00"
@"str_52" = constant [11 x i8] c"Algum > 3?\00"
@"str_53" = constant [3 x i8] c"%s\00"
define i64 @"__closure_4"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"icmp" = icmp sgt i64 %"x_load", 3
  %"closure_ret_zext" = zext i1 %"icmp" to i64
  ret i64 %"closure_ret_zext"
}

@"str_54" = constant [2 x i8] c" \00"
@"str_55" = constant [4 x i8] c"%ld\00"
@"str_56" = constant [2 x i8] c"\0a\00"
@"str_57" = constant [19 x i8] c"=== find_index ===\00"
@"str_58" = constant [3 x i8] c"%s\00"
@"str_59" = constant [2 x i8] c"\0a\00"
define i64 @"__closure_5"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"icmp" = icmp eq i64 %"x_load", 4
  %"closure_ret_zext" = zext i1 %"icmp" to i64
  ret i64 %"closure_ret_zext"
}

@"str_60" = constant [14 x i8] c"\c3\8dndice do 4:\00"
@"str_61" = constant [3 x i8] c"%s\00"
@"str_62" = constant [2 x i8] c" \00"
@"str_63" = constant [4 x i8] c"%ld\00"
@"str_64" = constant [2 x i8] c"\0a\00"
@"str_65" = constant [17 x i8] c"=== for_each ===\00"
@"str_66" = constant [3 x i8] c"%s\00"
@"str_67" = constant [2 x i8] c"\0a\00"
define i64 @"__closure_6"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"add" = add i64 %"x_load", 10
  ret i64 %"add"
}

@"str_68" = constant [17 x i8] c"Ap\c3\b3s +10, soma:\00"
@"str_69" = constant [3 x i8] c"%s\00"
@"str_70" = constant [2 x i8] c" \00"
@"str_71" = constant [4 x i8] c"%ld\00"
@"str_72" = constant [2 x i8] c"\0a\00"
@"str_73" = constant [16 x i8] c"=== reverse ===\00"
@"str_74" = constant [3 x i8] c"%s\00"
@"str_75" = constant [2 x i8] c"\0a\00"
@"str_76" = constant [33 x i8] c"Primeiro elemento ap\c3\b3s reverse:\00"
@"str_77" = constant [3 x i8] c"%s\00"
@"str_78" = constant [2 x i8] c" \00"
@"str_79" = constant [4 x i8] c"%ld\00"
@"str_80" = constant [2 x i8] c"\0a\00"